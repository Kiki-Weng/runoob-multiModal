主要实战内容包含了四个python脚本和一些其他资源。

runoob-vision-demo.py
是用来实现视觉理解的。
理解的是test_images里面的图片。使用的是DeepSeek的API，不够稳定。

runoob-glm-image-demo.py是进行文生图的练习。
生成的图片在runoob_generated_images里面，使用的API是智谱的，国内速度比较快。

runoob-glm-asr-demo.py是进行音频转文字ASR的练习，识别的音频是voice-sample.wav，它是单声道的。也是用智谱的模型。

runoob-image-analyzer.py是一个图片分析器。
分析的图片是runoob_test_image.jpg。分析的结果在runoob_analysis里面。使用的智谱的模型。

新增了一个简单的Webhook接收+AI处理流程脚本runoob-webHook.py。
这个脚本使用了Flask路由。
两种测试方法，本地网页和curl语句如图：
<img width="1874" height="909" alt="a78c029c2c705829313e73c775de34cd" src="https://github.com/user-attachments/assets/3409dd3b-0a9d-4038-bfd5-7b82f7dd8c1d" />
curl语句忘记截图了。
