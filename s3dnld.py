import os
import glob
import json
import random
from pathlib import Path
from difflib import SequenceMatcher
import cv2
import pandas as pd
import numpy as np
from PIL import Image
from tqdm import tqdm
from IPython.display import display
import matplotlib
from matplotlib import pyplot, patches



def read_bbox_and_words(path: Path):
    bbox_and_words_list = []
    with open(path, 'r', errors='ignore') as f:
        for line in f.read().splitlines():
            if len(line) == 0:
                continue
            split_lines = line.split(",")
            bbox = np.array(split_lines[0:8], dtype=np.int32)
            text = ",".join(split_lines[8:])
            bbox_and_words_list.append([path.stem, bbox, text])
    dataframe = pd.DataFrame(bbox_and_words_list,
                             columns=['filename', 'x0', 'y0', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'line'],
                             dtype=np.int16)
    dataframe = dataframe.drop(columns=['x1', 'y1', 'x3', 'y3'])
    return dataframe


def assign_line_label(line: str, entities: pd.DataFrame):
    line_set = line.replace(",", "").strip().split()
    for i, column in enumerate(entities):
        entity_values = entities.iloc[0, i].replace(",", "").strip()
        entity_set = entity_values.split()
        matches_count = 0
        for l in line_set:
            if any(SequenceMatcher(a=l, b=b).ratio() > 0.8 for b in entity_set):
                matches_count += 1
            if (column.upper() == 'ADDRESS' and (matches_count / len(line_set)) >= 0.5) or \
               (column.upper() != 'ADDRESS' and (matches_count == len(line_set))) or \
               matches_count == len(entity_set):
                return column.upper()
    return "O"

def assign_labels(words, entities):
    max_area = {"TOTAL": (0, -1), "DATE": (0, -1)}
    already_labeled = {"TOTAL": False,
                       "DATE": False,
                       "ADDRESS": False,
                       "COMPANY": False,
                       "O": False
    } 
    labels = []
    for i, line in enumerate(words['line']):
        label = assign_line_label(line, entities)  
        already_labeled[label] = True
        if (label == "ADDRESS" and already_labeled["TOTAL"]) or \
           (label == "COMPANY" and (already_labeled["DATE"] or already_labeled["TOTAL"])):
            label = "O"

        # Assign to the largest bounding box
        if label in ["TOTAL", "DATE"]:
            x0_loc = words.columns.get_loc("x0")
            bbox = words.iloc[i, x0_loc:x0_loc+4].to_list()
            area = (bbox[2] - bbox[0]) + (bbox[3] - bbox[1]) 
            if max_area[label][0] < area:
                max_area[label] = (area, i) 
            label = "O" 
        labels.append(label) 
    labels[max_area["DATE"][1]] = "DATE"
    labels[max_area["TOTAL"][1]] = "TOTAL" 
    words["label"] = labels
    return words

def dataset_creator(folder: Path):
  bbox_folder = folder/'box'
  entities_folder = folder/'entities'
  img_folder = folder/'img'
  entities_files = entities_folder.glob("*.txt")
  bbox_files =bbox_folder.glob("*.txt")
  img_files = img_folder.glob("*.jpg")
  data = []
  
  print("Reading dataset:")

def read_entities(entities_file):
    with open(entities_file, 'r') as file:
    entities_data = json.load(file)
return entities_data
    pass

def split_line(row):
    split_line=split_line
    pass

  for bbox_file, entities_file, img_file in tqdm(zip(bbox_files, entities_files, img_files), total=len(bbox_files)):            
    bbox = read_bbox_and_words(bbox_file)
    entities = read_entities(entities_file)
    image = Image.open(img_file)
    bbox_labeled = assign_labels(bbox, entities)
    del bbox
    new_bbox_l = []
    for index, row in bbox_labeled.iterrows():
      new_bbox_l += split_line(row)
    new_bbox = pd.DataFrame(new_bbox_l, columns=bbox_labeled.columns, dtype=np.int16)
    del bbox_labeled
    #Extra label assignment to incrase the precision of the labelling(can be omitted)
    for index, row in new_bbox.iterrows():
      label = row['label']
      if label != "O":
        entity_values = entities.iloc[0, entities.columns.get_loc(label.lower())]
        entity_set = entity_values.split()
        if any(SequenceMatcher(a=row['line'], b=b).ratio() > 0.7 for b in entity_set):
            label = "S-" + label
        else:
            label = "O"
      new_bbox.at[index, 'label'] = label
    width, height = image.size
    data.append([new_bbox, width, height])
  return data
pretrained_model_folder_input = r'C:\Users\GB Tech\Desktop\ocrapi\unilm\layoutlm\deprecated\layoutlm' / Path(
    'layoutlm-base-uncased')
pretrained_model_folder =Path('/layoutlm-base-uncased/')
label_file = Path(r'C:\Users\GB Tech\Desktop\ocrapi\unilm\layoutlm\deprecated\layoutlm\SROIE2019\test\entities',"labels.txt")