# PythonAnywhere WSGI 配置模板
# 复制此内容到 PythonAnywhere Web 页面的 WSGI 文件中
# 路径示例：/var/www/你的用户名_pythonanywhere_com_wsgi.py
#
# 使用前请替换：
# - 你的用户名
# - 仓库名/项目路径

# +++++++++++ ReMarket Django +++++++++++
import os
import sys

# 项目路径：包含 manage.py 的目录（请根据实际路径修改）
path = '/home/你的用户名/仓库名/Remarket/e-commerce-website-django-main'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'Commerce.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
