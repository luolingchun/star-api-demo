import os
import shutil
import sys

from Cython.Build import cythonize
from setuptools import Extension, setup

pythonpath = os.path.join(os.path.dirname(__file__), "src")

os.chdir(pythonpath)
sys.path.append(pythonpath)

if len(sys.argv) == 1:
    sys.argv.extend(["build_ext", "--inplace", "-j8"])


def c_compile(name, modules):
    """
    使用Cython进行编译
    :param str name: 项目名称
    :param list modules: [(module_name, source_file_path), (..., ...)]
    :return:
    """
    module_list = []
    for m in modules:
        module_list.append(Extension(name=m[0], sources=[m[1]]))
    setup(
        name=name,
        ext_modules=cythonize(
            module_list=module_list,
            language_level=3,  # python3
        ),
        zip_safe=False,
        install_requires=[
            "Cython",
        ],
    )


_modules = []
exclude_module_list = ["asgi", "bin.worker"]
# 遍历找到需要编译的py文件
for root, dirs, files in os.walk("."):
    if "migrations" in root:
        continue
    for file in files:
        if not file.endswith(".py"):
            continue
        file_path = os.path.join(root, file)
        _name = os.path.splitext(file_path)[0].replace(os.path.sep, ".").lstrip(".")
        if _name in exclude_module_list:
            continue
        print(_name, file_path)
        _modules.append((_name, file_path))

# 开始编译
c_compile("compile", _modules)
dist = "../dist"
os.makedirs(dist, exist_ok=True)
# 删除构建目录
shutil.rmtree("./build")
# 删除目标目录
shutil.rmtree("../dist")
# 拷贝编译后的文件
for root, dirs, files in os.walk("."):
    for _dir in dirs:
        if _dir == "__pycache__":
            shutil.rmtree(os.path.join(root, _dir))
    for file in files:
        file_path = os.path.join(root, file)
        _name = os.path.splitext(file_path)[0].replace(os.path.sep, ".").lstrip(".")
        if os.path.splitext(file)[-1] == ".c":
            os.remove(os.path.join(root, file))
        elif os.path.splitext(file)[-1] in [".pyd", ".so"]:
            # 移动编译文件到 dist
            dst_path = os.path.join(dist, file_path)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.move(file_path, dst_path)
        elif "migrations" in root:
            shutil.copytree(os.path.join(root, file), dist, dirs_exist_ok=True)
        elif _name in exclude_module_list:
            # 拷贝跳过编译的文件
            dst_path = os.path.join(dist, file_path)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy(file_path, dst_path)
