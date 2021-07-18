import os
import logging
import argparse
from xml.dom import minidom
from pycocotools.coco import COCO
import json


class Dataset():
    def __init__(self, jsonSrc, annFolder):
        super(Dataset, self).__init__()
        self.setLogger()  # Set log
        self.dom = minidom.Document()
        self.jsonSrc = jsonSrc
        self.annFloder = annFolder
        self.coco = COCO(self.jsonSrc)  # Load the data set to the COCO object

    def setLogger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.DEBUG)  # Set log level

        # FileHander will log output log file
        fileName = os.path.basename(__file__).split('.')[0]  # Set the log file name to the execution file name
        rootPath = os.path.abspath(".")
        logPath = os.path.join(rootPath, "log")  # Set the log file storage path
        if not os.path.exists(logPath):
            os.makedirs(logPath)
        logFileName = os.path.join(logPath, fileName + ".log")  # Full name of the log
        handler = logging.FileHandler(logFileName)  # Set file handler to output to file
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def createElementNode(self, nodeName, nodeText):
        """
                 Create node
                 :param nodeName: node name
                 :param nodeText: node content
                 :return: node
        """
        node = self.dom.createElement(nodeName)
        text = self.dom.createTextNode(str(nodeText))
        node.appendChild(text)
        return node

    def createSourceNode(self, sourceInfo):
        """
                 Package source node
                 :param sourceInfo: source node information (Dict{database:XXX, annotation:XXX....})
                 :return: source node
        """
        node = self.dom.createElement('source')
        node.appendChild(self.createElementNode('database', sourceInfo['database']))
        node.appendChild(self.createElementNode('annotation', sourceInfo['annotation']))
        node.appendChild(self.createElementNode('image', sourceInfo['image']))
        node.appendChild(self.createElementNode('flickrid', sourceInfo['flickrid']))
        return node

    def createOwnerNode(self, ownerInfo):
        """
                 Package owner node
                 :param ownerInfo: owner node information (Dict{flickrid:XX, name:XX})
                 :return: owner node
        """
        node = self.dom.createElement('owner')
        node.appendChild(self.createElementNode('flickrid', ownerInfo['flickrid']))
        node.appendChild(self.createElementNode('name', ownerInfo['name']))
        return node

    def createSizeNode(self, sizeInfo):
        """
                 Package size node
                 :param sizeInfo: size node information (Dict{width:XX, height:XX...})
                 :return: size node
        """
        node = self.dom.createElement('size')
        node.appendChild(self.createElementNode('width', sizeInfo['width']))
        node.appendChild(self.createElementNode('height', sizeInfo['height']))
        node.appendChild(self.createElementNode('depth', sizeInfo['depth']))
        return node

    def createObjectNode(self, objectInfo):
        """
                 Encapsulate object node
                 :param objectInfo: Information required by the object node (Dict(name:XX, pose:XX....))
                 :return: boject node
        """
        node = self.dom.createElement('object')
        node.appendChild(self.createElementNode('name', objectInfo['name']))
        node.appendChild(self.createElementNode('pose', objectInfo['pose']))
        node.appendChild(self.createElementNode('truncated', objectInfo['truncated']))
        node.appendChild(self.createElementNode('difficult', objectInfo['difficult']))
        bndboxNode = self.dom.createElement('bndbox')
        bndboxNode.appendChild(self.createElementNode('xmin', objectInfo['bndbox']['xmin']))
        bndboxNode.appendChild(self.createElementNode('ymin', objectInfo['bndbox']['ymin']))
        bndboxNode.appendChild(self.createElementNode('xmax', objectInfo['bndbox']['xmax']))
        bndboxNode.appendChild(self.createElementNode('ymax', objectInfo['bndbox']['ymax']))
        node.appendChild(bndboxNode)  # Add bndbox to the object node
        return node

    def genAnnotation(self, vocInfo):
        """
                 Anntation to create a single picture
                 :param vocInfo: VOC information of the picture (dictionary)
                 :return: XML node of annotation
        """
        annotationNode = self.dom.createElement('annotation')
        # folderNode build and add
        folderNode = self.createElementNode('folder', vocInfo['folder'])
        annotationNode.appendChild(folderNode)
        # filenameNode build and add
        filenameNode = self.createElementNode('filename', vocInfo['filename'])
        annotationNode.appendChild(filenameNode)
        # sourceNode build and add
        sourceNode = self.createSourceNode(vocInfo['sourceInfo'])
        annotationNode.appendChild(sourceNode)
        # ownerNode build and add
        ownerNode = self.createOwnerNode(vocInfo['ownerInfo'])
        annotationNode.appendChild(ownerNode)
        # sizeNode build and add
        sizeNode = self.createSizeNode(vocInfo['sizeInfo'])
        annotationNode.appendChild(sizeNode)
        # segmentedNode build and add
        segmentedNode = self.createElementNode('segmented', vocInfo['segmented'])
        annotationNode.appendChild(segmentedNode)
        # Create and add all objectNodes in a loop
        for objectInfo in vocInfo['objectInfo']:
            objectNode = self.createObjectNode(objectInfo)
            annotationNode.appendChild(objectNode)
        return annotationNode

    def genVocInfo(self, imgId):
        """
                 Generate the Voc information of a single picture according to the imgId in the coco data set
                 :param imgId: Image Id in the coco dataset
                 :return: voc information of the corresponding picture of imgId
        """
        vocInfo = {
            'folder': None,
            'filename': None,
            'sourceInfo': {
                'database': 'Detection',
                'annotation': 'COCOData',
                'image': 'flickr',
                'flickrid': 'NULL'
            },
            'ownerInfo': {
                'flickrid': 'NULL',
                'name': 'LY'
            },
            'sizeInfo': {
                'width': None,
                'height': None,
                'depth': None
            },
            'segmented': None,
            'objectInfo': []
        }  # Create a vocInfo dictionary to store the information needed by voc
        imageInfo = self.coco.loadImgs(ids=[imgId])[0]  # image information
        annotationsInfo = self.coco.loadAnns(ids=[imgId])  # Comment information
        vocInfo['folder'] = self.annFloder
        vocInfo['filename'] = imageInfo['file_name']  # Fill in the filename
        vocInfo['sizeInfo']['width'] = imageInfo['width']
        vocInfo['sizeInfo']['height'] = imageInfo['height']
        vocInfo['sizeInfo']['depth'] = 3
        vocInfo['segmented'] = 0
        # Traverse all the comments of the picture
        for anntation in annotationsInfo:
            objectInfo = {
                'name': None,
                'pose': 'Unspecified',
                'truncated': 0,
                'difficult': 0,
                'bndbox': {
                    'xmin': None,
                    'ymin': None,
                    'xmax': None,
                    'ymax': None
                }
            }  # Create an object dictionary to store information
            catInfo = self.coco.loadCats(ids=[anntation['category_id']])  # Classification information of the note
            bbox = anntation['bbox']  # Get the bounding box information of the annotation
            objectInfo['name'] = catInfo[0]['name']
            objectInfo['bndbox']['xmin'] = int(bbox[0])
            objectInfo['bndbox']['ymin'] = int(bbox[1])
            objectInfo['bndbox']['xmax'] = int(bbox[0]+bbox[2])
            objectInfo['bndbox']['ymax'] = int(bbox[1]+bbox[3])
            vocInfo['objectInfo'].append(objectInfo)
        return vocInfo

    def convertXML(self):
        savePath = annFolder + '/' + 'Annotations/'  # The file is generated under the current program folder
        if not os.path.exists(savePath):  # Create if there is no folder
            os.makedirs(savePath)
        imgIds = self.coco.getImgIds()  # Get the ID of all images
        print('There are {} images in {}'.format(len(imgIds), self.jsonSrc))
        for imgId in imgIds:  # Loop through each image id
            vocInfo = self.genVocInfo(imgId)  # Generate voc data based on coco image id
            annotationNode = self.genAnnotation(vocInfo)  # Generate xml format nodes based on voc data
            saveName = vocInfo['filename'].split('.')[0] + '.xml'  # Save the xml name to be consistent with the image name
            saveFile = savePath + saveName  # Save xml path
            try:
                with open(saveFile, 'w', encoding='utf-8') as f:  # save Picture
                    annotationNode.writexml(f, indent='', addindent='\t', newl='\n')
                print(saveFile, ' write ok')
            except Exception as e:
                self.logger.error("Write Xml ERROR: %s failed\n Exception as follow: %s "
                                  % (saveName, e))
                print("\033[31mError: %s wrote failed!\033[0m" % saveName)


if __name__ == '__main__':
    label = 'test'
    annFolder = '/media/kisna/work_1/flirDataSet/annotation_test/images'

    # jsonPath = '../../../{}/landslide_{}_google_20191115.json'.format(label, label)
    jsonPath = '/media/kisna/work_1/flirDataSet/annotation_test/images/thermal_annotations.json'
    data = Dataset(jsonPath, annFolder)
    data.convertXML()

