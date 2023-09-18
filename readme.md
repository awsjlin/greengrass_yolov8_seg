
# AWS IoT Greengrass ONNX YOLOv8 Instance Segmentation component
A real-time, webcam python script as a custom AWS IoT Greengrass component in Greengrass v2 performing instance segmentation using the YOLOv8 model in ONNX on a Raspberry Pi 4. The component also publishes MQTT data to AWS IoT Core on on the object detected with box coordinates from the image and launches an OpenCV GUI to show the visualization at the edge.


![! ONNX YOLOv8 Instance Segmentation](/resources/detected_objects.jpg)
# Solution Architecture
![! Architecture](/resources/architecture.png)
# Requirements

 * An AWS account. [Set up an AWS account](https://docs.aws.amazon.com/greengrass/v2/developerguide/setting-up.html#set-up-aws-account) if you need one.
 * An AWS Identity and Access Mangement (IAM) user with Administrator permissions.
 * A physical device with at least the specifications of a [Raspberry Pi](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) and a microSDHC.
   * To set up your Raspberry Pi, please [follow these steps](https://catalog.workshops.aws/aws-iot-immersionday-workshop/en-US/aws-greengrassv2/greengrass-physicaldevice/lab37-rpi-greengrass-basics) for Step 1 & Step 2.
 * Either a USB web camera or a Raspberry Pi Camera Module.
     * For **Raspberry Pi Camera Module**: The Python Picamera module is not, by default, compatible with the latest version of Raspberry Pi OS. [To use the Picamera module, you will need to enable legacy support for the camera.](https://youtu.be/E7KPSc_Xr24)

 * **Important**: For the Raspberry Pi, use the **Raspberry Pi OS (64-bit)** image, not the default version. This is critical to be able to install onnxruntime.
 * **Note**: (If not using a Raspberry Pi) After the  *git clone* below, please check the `requirements.txt` file in the /artifact directory.
   * For ONNX, if you have a NVIDIA GPU, then install the `onnxruntime-gpu`, otherwise use the `onnxruntime` library.
   * *This example is based off of the Raspberry Pi 4 running the Raspberry Pi OS (64-bit) is using **onnxruntime**.*

# Installation
```
git clone https://github.com/awsjlin/greengrass_yolov8_seg.git
```
1. Create a S3 bucket to upload the artifacts.
2. Upload files to S3
   * `aws S3 cp --recursive <../greengrass-onnx-instance-segmentation-directory/artifact> S3://<your_bucket>`
3. Modify the role for your core device, usually `GreengrassV2TokenExchangeRole` to allow the action of `s3:GetObject`.
   * See the example shown in instruction 2. of [Create your component in the AWS IoT Greengrass service.](https://docs.aws.amazon.com/greengrass/v2/developerguide/upload-first-component.html)
4. Update the **objSegRecipe.json** `"Artifacts"` `"URI"`s to the *S3 URI* from your bucket.

**Optional configurations:**

1. *To change the topic*, edit the file **webcam_instance_segmentation.py** in the **/artifact** directory with the variable:
   * `topic = "objDetect/topic"`
2. *The YOLOv8 instance segmentation model can be updated to a larger size* from the Ultralytics link below. If upgrading to a higher resolution model:
   1. Download the [YOLOv8 Segmentation model](https://github.com/ultralytics/ultralytics) of choice from Ultralytics.
   2. Replace the **yolov8n-seg.onnx** file the S3 bucket with the downloaded file.
   3. Replace the the `yolov8n-seg.onnx` argument in **objSegRecipe.json** Recipe and the `URI` under `"Artifacts"` to match your new model's S3 URI.
     * `--model={artifacts:path}/yolov8n-seg.onnx"`
       * Note: The input images are directly resized to match the input size of the model. It might affect the accuracy of the model if the input image has a different aspect ratio compared to the input size of the model. Always try to get an input size with a ratio close to the input images you will use.

## Publish


Using the AWS CLI:

```
aws greengrassv2 create-component-version --inline-recipe fileb://./objSegRecipe.json --region <your_region>
```
**Important**
Before deploying `community.greengrass.objSeg`, you must **Configure component** so the custom component has access to launch the local OpenCV GUI on the device.

From the AWS Console:
1. In the AWS IoT → Greengrass → Deployments menu, select the `community.greengrass.objSeg` component and click the **Configure component** button.
2. Then expand the **Advanced configuration** area. Under **Linux system user**, enter in `1000`. Under **Linux system group**, enter in `1000`. [See here for reference](/resources/configure_component.png).

From the command line:
1. In a [deployment JSON file](/resources/deployment.json), be sure to add the **posixUser** value of `"1000:1000"` this under `"components"`:
    ```
        "community.greengrass.objSeg": {
            "componentVersion": "1.0.0",
            "runWith": {
                "posixUser": "1000:1000"
            }
        }
    ```
2. Create the deployment with your deployment template.
     ```
     /usr/local/bin/aws greengrassv2 create-deployment --cli-input-json file://deployment.json --region <region>
     ```
## Logs

The Greengrass component log can be found accessed as follows:

```
sudo tail -f /greengrass/v2/logs/community.greengrass.objSeg.log
```

# Testing

This component has been tested on a **Raspberry Pi 4** with the **Raspberry Pi OS (64-bit)**. An OpenCV GUI should launch on the device on successful deployment.

1. To see the payload results, log into the AWS Console, go to **AWS IoT Core**, and navigate to ```Test``` → ```MQTT test client```.
2. Subscribe to ```objDetect/topic``` (or the updated topic, if updated).

An example of the payload output in the **AWS IoT Core MQTT test client**:

```
[
  {
    "id": "laptop",
    "score": 0.6372153162956238,
    "box": [
      0.4095916748046875,
      117.48372650146484,
      193.8508758544922,
      368.5118713378906
    ],
    "timestamp": "2023-07-10 03:18:09.355839"
  },
  {
    "id": "mouse",
    "score": 0.6336110830307007,
    "box": [
      103.9091567993164,
      323.7207336425781,
      321.7975158691406,
      409.0905456542969
    ],
    "timestamp": "2023-07-10 03:18:09.355905"
  },
  {
    "id": "keyboard",
    "score": 0.36082178354263306,
    "box": [
      122.99805450439453,
      262.7191162109375,
      306.26220703125,
      337.076171875
    ],
    "timestamp": "2023-07-10 03:18:09.355920"
  }
]
```

# License: ONNX model & base scripts License
- The License of the models is GPL-3.0 license: [License](https://github.com/ultralytics/ultralytics/blob/master/LICENSE)
- The base code from Ibai Gorodo is a MIT license: [License](https://github.com/ibaiGorordo/ONNX-YOLOv8-Instance-Segmentation/blob/main/LICENSE)

# Original YOLOv8 model
The original YOLOv8 Instance Segmentation model can be found in this repository: [YOLOv8 Instance Segmentation](https://github.com/ultralytics/ultralytics)

# References
* YOLOv8 model: https://github.com/ultralytics/ultralytics
* ONNX-YOLOv8-Instance-Segmentation from Ibai Gorodo: https://github.com/ibaiGorordo/ONNX-YOLOv8-Instance-Segmentation/blob/main/README.md

## Acknowledgment
* Much thanks to [Greg Biegel](https://github.com/changamire) for QA testing this custom component.

## Support
Contact [Jennifer Lin](https://github.com/awsjlin) for questions or support help.