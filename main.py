import os
import urllib3

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


COMMON_IMAGE_EXTENSIONS = {
    "jpeg": "jpg",
    "jpg": "jpg",
    "pjpeg": "jpg",
    "png": "png",
    "gif": "gif",
    "webp": "webp",
    "bmp": "bmp",
    "svg+xml": "svg",
    "tiff": "tiff",
    "heic": "heic",
    "heif": "heif",
    "avif": "avif",
    "x-icon": "ico",
    "vnd.microsoft.icon": "ico",
}


def create_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        status=5,
        backoff_factor=0.5,
        status_forcelist=(408, 429, 500, 502, 503, 504),
        allowed_methods=("HEAD", "GET"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 12; Pixel 6 Pro) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
            ),
            "Referer": "https://www.douyin.com/",
        }
    )
    return session


def download_images():
    # 定义文件路径
    urls_file = 'urls.txt'
    images_dir = 'images/'
    session = create_session()

    # 确保 images 文件夹存在
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    # 读取 urls.txt 文件
    try:
        with open(urls_file, 'r') as file:
            urls = file.readlines()
    except FileNotFoundError:
        print(f"错误: 文件 {urls_file} 未找到！")
        return

    # 下载每个 URL 的图片
    for index, url in enumerate(urls):
        url = url.strip()  # 去掉换行符
        if not url:
            continue  # 跳过空行

        response = None
        try:
            try:
                response = session.get(url, stream=True, timeout=(5, 30))
                response.raise_for_status()  # 检查请求是否成功
            except requests.exceptions.SSLError as ssl_error:
                print(f"SSL 握手失败，尝试关闭验证后重试: {url} 错误: {ssl_error}")
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                # 某些源会提前终止 TLS 握手，这里降级关闭证书校验后重试一次
                response = session.get(url, stream=True, timeout=(5, 30), verify=False)
                response.raise_for_status()

            content_type_header = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
            extension = "jpg"
            if content_type_header.startswith("image/"):
                subtype = content_type_header.split("/", 1)[1]
                extension = COMMON_IMAGE_EXTENSIONS.get(subtype, subtype if subtype in COMMON_IMAGE_EXTENSIONS.values() else "jpg")

            filename = f"{index + 1}.{extension}"

            # 保存图片到 images 文件夹
            image_path = os.path.join(images_dir, filename)
            with open(image_path, 'wb') as image_file:
                for chunk in response.iter_content(1024):
                    if chunk:
                        image_file.write(chunk)

            print(f"成功下载: {url} -> {image_path}")
        except requests.RequestException as e:
            print(f"下载失败: {url} 错误: {e}")
        finally:
            if response is not None:
                response.close()


if __name__ == "__main__":
    download_images()
