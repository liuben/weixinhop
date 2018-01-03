# weixinhop
微信小游戏跳一跳的自动化脚本
目前没发现会跳不中的情况，大约90%的可能性会跳到中心。
*注意：纯属娱乐！刷分刷多了，会被微信禁号的哦！*

## 使用方法
1. 准备一台 Android 手机，usb线连电脑，打开调试模式
1. 电脑安装 Android sdk，需要使用其中的 adb
1. 电脑安装 python 2.7，安装 Pillow 库
1. 修改脚本中的 imgPath 以指定一个电脑上的临时路径，建议新建一个
1. 修改脚本中的 phonePath 以指定一个手机上的临时路径，建议新建一个
1. 如果手机屏幕不是 1080×1920 ，则需要进入调试模式，并修改脚本中的两个参数，调试模式详见后文。还需要截取一幅棋子的特征图。
1. 启动微信跳一跳，进入第一步跳之前的画面即可
1. 启动脚本 ./c.py，如无意外，大约几秒钟会跳一步

## 调试模式
调试模式用于分解执行每一步操作。如果手机屏幕不是 1080×1920，则需要先进入调试模式，手动尝试两个参数：标准距离和触摸时间。

./c.py -d 即可进入调试模式，可见提示 next: 。

调试模式支持以下命令：

1. shot 将当前手机屏幕截图并拖到电脑上
1. debug 对刚拖上来的截图进行分析，会输出目标点坐标、起点坐标以及两点之间的距离
1. jump 700 触摸屏幕指定长度的时间，以让棋子跳跃，此处的 700 可任意修改，单位是毫秒
1. 直接敲回车，则自动完成 shot、debug，并根据脚本中的预设值计算触摸时间，进而 jump

对于手机不是 1080×1920 的情况，需要尝试出在某个距离下，跳到中心所需的触摸时间。建议在游戏开始时的第一步进行反复尝试，因为第一步的距离基本都是固定的。所以，实际步骤是启动微信，然后 shot 和 debug ，记住 debug 输出的距离。然后用 jump 进行尝试，如果成功跳到中心，则将 debug 输出的距离写到脚本中的 STANDARD_DISTANCE 处，将 jump 设的触摸时间写到脚本中的 STANDARD_DURATION 处；如果 jump 尝试不成功，则重启游戏再次来到第一步，重新估算 jump 所需的值。

## 截取棋子的特征图

从任一屏幕截图中，分析一下棋子底部的中心点位置。建议用游戏开始时的截图，此时棋子本身就在正方体的中心，根据正方体的角的坐标可算出棋子中心的坐标。

然后用 python 命令行进行截图，例子如下所示：

``` python

>>> from PIL import Image
>>> im=Image.open("filepath/1.png")  # filepath 为目标
>>> c = [100,400] # 棋子底部中心点坐标
>>> box = [c[0]-24,c[1]-15,c[0]+24,c[1]+15] # 24 和 15 为例子，需要调整以让截出来的图完全在棋子内部
>>> imcrop = im.crop(box)
>>> imcrop.save("filepath/ball.png")

```

将 ball.png 存在 c.py 所在目录

## 测试模式
本项目中有一些测试图，用于测试特殊情况是否能正常运行。

./c.py -t test.txt 会进入测试模式，类似于单元测试。

test.txt 中记录了每张图的名称及其目标点的坐标。测试模式会对其进行比对。目前有两张图会略有偏差。

大家发现有计算不正确的情况，也可以将特征图加到测试用例中。

## 日志模式

./c.py -l

和直接 ./c.py 基本完全一样，会自动开始不断的跳。但会把每一步的截图都保存下来，以备后续调试所用。

## 原理解释



