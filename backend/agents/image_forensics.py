"""
ADFF - Image Forensics Agent
Computes Error Level Analysis (ELA), Local Noise Inconsistency, Edge Continuity Discontinuity,
and Keypoint Copy-Move Block Matching across document page images.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import cv2
from PIL import Image, ImageChops, ImageEnhance


class ImageForensicsAgent:
    def __init__(self, quality: int = 90, ela_scale: float = 18.0):
        self.quality = quality
        self.ela_scale = ela_scale

    def analyze_page(
        self,
        page_image_path: str,
        output_dir: str,
        page_idx: int = 0,
        understanding_res: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Runs comprehensive image forensic pipeline on a single page image.
        Outputs ELA heatmap, noise inconsistency metrics, edge continuity metrics, and copy-move indicators.
        """
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        img_bgr = cv2.imread(page_image_path)
        if img_bgr is None:
            raise FileNotFoundError(f"Cannot open page image at '{page_image_path}'.")

        h, w, c = img_bgr.shape
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        has_vector_text = understanding_res.get("has_vector_text", False) if understanding_res else False
        has_raster_images = understanding_res.get("has_raster_images", False) if understanding_res else False
        embedded_zones = understanding_res.get("embedded_image_zones", []) if understanding_res else []

        # 1. Error Level Analysis (ELA)
        ela_np, ela_gray, ela_mean, ela_max, ela_std = self._compute_ela(page_image_path, out_dir, page_idx)

        # 2. Local Noise Inconsistency
        noise_mean, noise_std, noise_ratio, noise_anomaly_score, noise_clusters = self._compute_noise_inconsistency(
            img_gray, is_vector_doc=(has_vector_text and not has_raster_images)
        )

        # 3. Edge Continuity & Boundary Discontinuity
        edge_discontinuity_score = self._compute_edge_continuity(img_gray)

        # 4. Copy-Move / Cloning Detection
        copy_move_detected, match_count = self._detect_copy_move(img_gray)

        # 5. Extract Suspicious Clusters from ELA and Embedded Zones
        ela_clusters = []

        # If PDF has embedded raster image objects (like a patched financial total or pasted signature)
        for ez in embedded_zones:
            if ez.get("page", 0) == page_idx:
                ez_box = ez["bbox"]
                x0 = max(0, min(w - 1, ez_box[0]))
                y0 = max(0, min(h - 1, ez_box[1]))
                x1 = max(0, min(w, ez_box[2]))
                y1 = max(0, min(h, ez_box[3]))
                if (x1 - x0) > 15 and (y1 - y0) > 8:
                    patch = ela_gray[y0:y1, x0:x1]
                    p_mean = float(np.mean(patch)) if patch.size > 0 else 0.0
                    ela_clusters.append({
                        "bbox": [x0, y0, x1, y1],
                        "area": (x1 - x0) * (y1 - y0),
                        "mean_ela_energy": max(78.0, p_mean),
                        "confidence": 0.95,
                        "source": "embedded_raster_patch_anomaly"
                    })

        # For pure image scans (not digital vector PDFs), extract high-residual dense clusters
        if not has_vector_text:
            dense_ela_clusters = self._extract_ela_clusters(ela_gray, img_bgr.shape)
            ela_clusters.extend(dense_ela_clusters)

        # Merge ELA clusters and Noise clusters
        all_clusters = self._merge_clusters(ela_clusters, noise_clusters)

        # Filter to confident clusters (>= 0.65) and take top 4
        all_clusters = [c for c in all_clusters if c.get("confidence", 0) >= 0.65]
        all_clusters.sort(key=lambda c: c.get("confidence", 0), reverse=True)
        all_clusters = all_clusters[:4]

        # 6. Generate and save false-color Thermal Heatmap
        heatmap_path = out_dir / f"forensic_heatmap_p{page_idx}.png"
        ela_normalized = cv2.normalize(ela_gray, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_color = cv2.applyColorMap(ela_normalized, cv2.COLORMAP_INFERNO)

        gray_3ch = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
        blended = cv2.addWeighted(heatmap_color, 0.65, gray_3ch, 0.35, 0)
        cv2.imwrite(str(heatmap_path), blended)

        # Anomaly score
        if all_clusters:
            top_cluster_conf = max(c.get("confidence", 0.5) for c in all_clusters)
            ela_anomaly_score = float(min(1.0, 0.45 + (top_cluster_conf * 0.45)))
        else:
            ela_anomaly_score = float(min(0.12, (ela_mean / 40.0) * 0.10))

        return {
            "page_index": page_idx,
            "dimensions": {"width": w, "height": h},
            "ela_mean_residual": float(round(ela_mean, 2)),
            "ela_max_residual": float(round(ela_max, 2)),
            "ela_std_residual": float(round(ela_std, 2)),
            "ela_anomaly_score": float(round(ela_anomaly_score, 3)),
            "noise_variance_mean": float(round(noise_mean, 2)),
            "noise_variance_std": float(round(noise_std, 2)),
            "noise_inconsistency_score": float(round(noise_anomaly_score, 3)),
            "edge_gradient_discontinuity_score": float(round(edge_discontinuity_score, 3)),
            "copy_move_detected": copy_move_detected,
            "copy_move_matches": match_count,
            "anomalous_clusters": all_clusters,
            "ela_image_path": str(out_dir / f"ela_p{page_idx}.png"),
            "heatmap_image_path": str(heatmap_path)
        }

    def _compute_ela(self, image_path: str, out_dir: Path, page_idx: int) -> Tuple[np.ndarray, np.ndarray, float, float, float]:
        orig_img = Image.open(image_path).convert("RGB")
        temp_jpg_path = out_dir / f"_temp_recomp_p{page_idx}.jpg"

        orig_img.save(temp_jpg_path, "JPEG", quality=self.quality)
        recompressed = Image.open(temp_jpg_path).convert("RGB")

        diff = ImageChops.difference(orig_img, recompressed)

        if temp_jpg_path.exists():
            temp_jpg_path.unlink()

        enhancer = ImageEnhance.Brightness(diff)
        ela_amplified = enhancer.enhance(self.ela_scale)

        ela_save_path = out_dir / f"ela_p{page_idx}.png"
        ela_amplified.save(ela_save_path)

        ela_np = np.array(ela_amplified)
        ela_gray = cv2.cvtColor(ela_np, cv2.COLOR_RGB2GRAY)

        mean_val = float(np.mean(ela_gray))
        max_val = float(np.max(ela_gray))
        std_val = float(np.std(ela_gray))

        return ela_np, ela_gray, mean_val, max_val, std_val

    def _compute_noise_inconsistency(
        self, gray: np.ndarray, is_vector_doc: bool = False
    ) -> Tuple[float, float, float, float, List[Dict[str, Any]]]:
        if is_vector_doc:
            return 0.0, 0.0, 1.0, 0.0, []

        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        h, w = gray.shape
        block_size = 48
        variances = []
        block_coords = []

        for y in range(0, h - block_size, block_size):
            for x in range(0, w - block_size, block_size):
                patch = laplacian[y:y + block_size, x:x + block_size]
                gray_patch = gray[y:y + block_size, x:x + block_size]
                if np.std(gray_patch) > 3.5:
                    var = float(np.var(patch))
                    variances.append(var)
                    block_coords.append((x, y, var))

        if len(variances) < 6:
            return 0.0, 0.0, 1.0, 0.0, []

        v_mean = float(np.mean(variances))
        v_std = float(np.std(variances))
        v_median = float(np.median(variances)) + 1e-4

        outlier_blocks = []
        for x, y, var in block_coords:
            ratio = var / v_median
            if ratio > 3.5 or ratio < 0.25:
                conf = min(0.95, 0.70 + (abs(ratio - 1.0) / 10.0) * 0.25)
                outlier_blocks.append({
                    "bbox": [x, y, x + block_size, y + block_size],
                    "mean_ela_energy": float(min(180.0, var / 30.0)),
                    "confidence": float(round(conf, 2)),
                    "reason": f"Noise variance disparity (var={var:.1f}, baseline={v_median:.1f})"
                })

        coalesced = self._coalesce_blocks(outlier_blocks, w, h)
        max_ratio = (max(variances) / v_median) if variances else 1.0
        anomaly_score = float(min(1.0, max(0.0, (max_ratio - 2.5) / 8.0)))

        return v_mean, v_std, float(max_ratio), anomaly_score, coalesced

    def _compute_edge_continuity(self, gray: np.ndarray) -> float:
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        grad_mag = np.sqrt(sobelx**2 + sobely**2)
        grad_std = float(np.std(grad_mag))
        return min(1.0, grad_std / 75.0)

    def _detect_copy_move(self, gray: np.ndarray) -> Tuple[bool, int]:
        orb = cv2.ORB_create(nfeatures=600)
        kp, des = orb.detectAndCompute(gray, None)

        if des is None or len(des) < 20:
            return False, 0

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        matches = bf.knnMatch(des, des, k=2)

        good_matches = []
        for m_pair in matches:
            if len(m_pair) == 2:
                m, n = m_pair
                if m.queryIdx != m.trainIdx:
                    pt1 = kp[m.queryIdx].pt
                    pt2 = kp[m.trainIdx].pt
                    dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
                    if dist > 70 and m.distance < 0.65 * n.distance:
                        good_matches.append(m)

        detected = len(good_matches) >= 8
        return detected, len(good_matches)

    def _extract_ela_clusters(self, ela_gray: np.ndarray, shape: Tuple[int, ...]) -> List[Dict[str, Any]]:
        h, w = shape[:2]
        non_zero = ela_gray[ela_gray > 4]
        if len(non_zero) < 50:
            return []

        nz_mean = float(np.mean(non_zero))
        nz_std = float(np.std(non_zero))

        high_thresh_val = max(130, int(nz_mean + (2.5 * nz_std)))
        _, thresh = cv2.threshold(ela_gray, high_thresh_val, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 20))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        clusters = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 800 < area < (h * w * 0.35):
                x, y, cw, ch = cv2.boundingRect(cnt)
                if cw > 40 and ch > 20:
                    patch = ela_gray[y:y + ch, x:x + cw]
                    mean_energy = float(np.mean(patch))
                    conf = min(0.96, max(0.70, mean_energy / 120.0))
                    clusters.append({
                        "bbox": [x, y, x + cw, y + ch],
                        "area": int(area),
                        "mean_ela_energy": float(round(mean_energy, 2)),
                        "confidence": float(round(conf, 2)),
                        "source": "ela"
                    })

        clusters.sort(key=lambda c: c["mean_ela_energy"], reverse=True)
        return clusters[:4]

    def _coalesce_blocks(self, blocks: List[Dict[str, Any]], w: int, h: int) -> List[Dict[str, Any]]:
        if not blocks:
            return []

        mask = np.zeros((h, w), dtype=np.uint8)
        for b in blocks:
            x0, y0, x1, y1 = b["bbox"]
            mask[y0:y1, x0:x1] = 255

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (60, 60))
        joined = cv2.dilate(mask, kernel, iterations=1)

        contours, _ = cv2.findContours(joined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        coalesced = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 1400:
                x, y, cw, ch = cv2.boundingRect(cnt)
                coalesced.append({
                    "bbox": [x, y, x + cw, y + ch],
                    "area": int(area),
                    "mean_ela_energy": 90.0,
                    "confidence": 0.90,
                    "source": "noise_inconsistency"
                })

        return coalesced

    def _merge_clusters(self, c1: List[Dict[str, Any]], c2: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        combined = list(c1)
        for item in c2:
            box = item["bbox"]
            merged = False
            for existing in combined:
                if self._iou(box, existing["bbox"]) > 0.25:
                    existing["confidence"] = max(existing["confidence"], item["confidence"])
                    existing["mean_ela_energy"] = max(existing.get("mean_ela_energy", 0), item.get("mean_ela_energy", 0))
                    merged = True
                    break
            if not merged:
                combined.append(item)

        return combined

    def _iou(self, boxA: List[int], boxB: List[int]) -> float:
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-5)
        return iou
