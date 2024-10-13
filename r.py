import os
import subprocess
from datetime import datetime
import pytz
from pathlib import Path


def convertDate(MediaCreateDateText):
    # 截取日期部分
    media_datetime = MediaCreateDateText[34:53]

    # 解析时间字符串为 datetime 对象
    time_obj = datetime.strptime(media_datetime, "%Y:%m:%d %H:%M:%S")

    # 假设这是 UTC 时间，转换为本地时间
    utc_time = pytz.utc.localize(time_obj)
    local_tz = pytz.timezone("Asia/Shanghai")  # 你可以根据需要更改时区
    local_time = utc_time.astimezone(local_tz)

    # 返回 YYYY-MM-DD 格式的字符串，如 2019-11-06
    return local_time.strftime("%Y-%m-%d")


# 使用 exiftool 获取媒体创建日期
def get_metadata(file_path, type):
    arg1 = ""
    if type == ".mp4":
        arg1 = "-MediaCreateDate"
    if type == ".mkv":
        arg1 = "-DateTimeOriginal"

    result = subprocess.run(
        ["exiftool", arg1, file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout
    else:
        print(f"Error: {result.stderr}")


# 递归遍历当前文件夹中的所有 mp4 和 mkv 文件，并重命名
folder_path = Path(".")
for file_path in folder_path.rglob("*"):
    if file_path.is_file():
        if file_path.suffix in [".mp4", ".mkv"]:

            MediaCreateDateStr = get_metadata(file_path.resolve(), file_path.suffix)
            if MediaCreateDateStr:
                # print(MediaCreateDateStr)
                # mp4 文件的值如下：
                # Media Create Date               : 2019:11:05 16:51:52
                # 从 iwara 下载的 mp4 视频没有实际的媒体创建日期，值全是 0:
                # Media Create Date               : 0000:00:00 00:00:00
                # mkv 文件的值如下：
                # Date/Time Original              : 2024:10:03 08:14:07Z
                # 如果文件没有要查找的属性，则值是 None

                if "0000" in MediaCreateDateStr:
                    print("该文件的媒体创建日期无效：" + file_path.name)
                    continue

                localDate = convertDate(MediaCreateDateStr)
                # print(localDate)
                # 2019-11-06

                os.rename(file_path.name, localDate + " " + file_path.name)
            else:
                print("该文件没有找到媒体创建日期：" + file_path.name)
