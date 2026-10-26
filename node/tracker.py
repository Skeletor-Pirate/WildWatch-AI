import numpy as np

def bbox_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    return inter_area / float(box1_area + box2_area - inter_area + 1e-6)

class ObjectTracker:
    def __init__(self, iou_thresh=0.3):
        self.tracks = {}
        self.next_id = 0
        self.iou_thresh = iou_thresh

    def update(self, detections):
        updated_tracks = []
        unmatched_dets = list(detections)
        
        for track_id, track in list(self.tracks.items()):
            best_iou = 0
            best_det = None
            for det in unmatched_dets:
                iou = bbox_iou(track['bbox'], det['bbox'])
                if iou > best_iou:
                    best_iou = iou
                    best_det = det
                    
            if best_iou > self.iou_thresh:
                track['bbox'] = best_det['bbox']
                track['conf'] = best_det['conf']
                track['class'] = best_det['class']
                track['history'].append(self._get_centroid(best_det['bbox']))
                updated_tracks.append(track)
                unmatched_dets.remove(best_det)
            else:
                del self.tracks[track_id]
                
        for det in unmatched_dets:
            new_track = {
                'id': self.next_id,
                'bbox': det['bbox'],
                'class': det['class'],
                'conf': det['conf'],
                'history': [self._get_centroid(det['bbox'])]
            }
            self.tracks[self.next_id] = new_track
            updated_tracks.append(new_track)
            self.next_id += 1
            
        return updated_tracks

    def _get_centroid(self, bbox):
        return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)