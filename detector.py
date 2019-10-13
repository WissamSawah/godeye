
import tensorflow as tf
import numpy as np
from PIL import Image
from PIL import ImageDraw
from object_detection.utils import visualization_utils as vis_util
from werkzeug.datastructures import CombinedMultiDict
from wtforms import Form
from wtforms import ValidationError
from cv2 import imencode
from app_utils import draw_boxes_and_labels
from object_detection.utils import label_map_util
from MySQLdb import escape_string as thwart

PATH_TO_CKPT = 'frozen_inference_graph.pb'
PATH_TO_LABELS = 'mscoco_label_map.pbtxt'

class ObjectDetector(object):

  def __init__(self):
    self.detection_graph = self._build_graph()
    self.sess = tf.compat.v1.Session(graph=self.detection_graph)

    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=90, use_display_name=True)
    self.category_index = label_map_util.create_category_index(categories)

  def _build_graph(self):
    detection_graph = tf.Graph()
    with detection_graph.as_default():
      od_graph_def = tf.compat.v1.GraphDef()
      with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    return detection_graph
