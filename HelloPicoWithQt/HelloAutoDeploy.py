import subprocess
import shutil
import logging
import os
import sys
import traceback


def subprocess_call(args_list: list, need_result: bool = True):
    if need_result:
        try:
            result = subprocess.run(args_list, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return result.stdout
        except Exception as e:
            logging.exception(traceback.format_exc())
        return None
    else:
        # 这里不加try, 错了就立刻停止后续代码的执行
        subprocess.run(args_list, text=True, check=False)


result = subprocess.run([shutil.which("git"), "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
if result.returncode != 0:
    logging.error("Git tag获取失败，查看机器是否有git")
    sys.exit(-1)
git_head = result.stdout[:7]

now_script_path = os.path.dirname(os.path.abspath(__file__))
main_file_path = os.path.join(now_script_path, "main.py")

package_name = "HelloPicoWithQt-{}".format(git_head)
dist_path = os.path.join(now_script_path, "dist")
actually_build_path = os.path.join(dist_path, "{}.build".format(package_name))
actually_dist_path = os.path.join(dist_path, "{}.dist".format(package_name))
if os.path.exists(actually_dist_path):
    shutil.rmtree(actually_dist_path)  # 减少bug
os.makedirs(dist_path, exist_ok=True)

pyinstaller_path = shutil.which("pyinstaller")
pyinstaller_command = [
    pyinstaller_path, "-y",
    "--log-level", "INFO",
    "--workpath", actually_build_path,
    "--distpath", actually_dist_path,
    "-D", "--contents-directory", ".",
    main_file_path
]

subprocess_call(pyinstaller_command, need_result=False)

wait_copy_list = ["main.qml", "Components"]
for each_copy in wait_copy_list:
    abs_path = os.path.join(now_script_path, each_copy)
    if os.path.isfile(abs_path):
        shutil.copy(abs_path, actually_dist_path)
    else:
        shutil.copytree(abs_path, os.path.join(actually_dist_path, each_copy))

main_folder = os.path.join(actually_dist_path, "main")
if not os.path.exists(os.path.join(main_folder, "main.exe")):
    logging.error("Pyinstaller打包失败，查看日志看看出什么问题了")
    sys.exit(-1)

logging.info("拷贝结构树")
shutil.copytree(main_folder, actually_dist_path, dirs_exist_ok=True)
shutil.rmtree(main_folder)
logging.info("打包结束")