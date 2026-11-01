import requests

#resp = requests.get("https://httpbin.org/get")
#print(f"状态码: {resp.status_code}")
#print(f"响应内容: {resp.json()}")


#实验A
# try:
#     requests.get('https://httpbin.org/delay/10', timeout=3)
# except Exception as e:
#     print(type(e).__name__)
#     print('response =', getattr(e, 'response', 'NO_ATTR'))

# 结果A：
# C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Scripts\python.exe C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\ex1_1.py
# ReadTimeout
# response = None
    
#实验B

# r=requests.get('https://httpstat.us/504'); print(r.status_code)
#
# 结果B：
# Traceback (most recent call last):
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\urllib3\connectionpool.py", line 793, in urlopen
#     response = self._make_request(
#                ^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\urllib3\connectionpool.py", line 540, in _make_request
#     response = conn.getresponse()
#                ^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\urllib3\connection.py", line 638, in getresponse
#     httplib_response = super().getresponse()
#                        ^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\http\client.py", line 1430, in getresponse
#     response.begin()
#   File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\http\client.py", line 331, in begin
#     version, status, reason = self._read_status()
#                               ^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\http\client.py", line 300, in _read_status
#     raise RemoteDisconnected("Remote end closed connection without"
# http.client.RemoteDisconnected: Remote end closed connection without response
#
# During handling of the above exception, another exception occurred:
#
# Traceback (most recent call last):
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\requests\adapters.py", line 696, in send
#     resp = conn.urlopen(
#            ^^^^^^^^^^^^^
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\urllib3\connectionpool.py", line 847, in urlopen
#     retries = retries.increment(
#               ^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\urllib3\util\retry.py", line 510, in increment
#     raise reraise(type(error), error, _stacktrace)
#           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\urllib3\util\util.py", line 38, in reraise
#     raise value.with_traceback(tb)
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\urllib3\connectionpool.py", line 793, in urlopen
#     response = self._make_request(
#                ^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\urllib3\connectionpool.py", line 540, in _make_request
#     response = conn.getresponse()
#                ^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\urllib3\connection.py", line 638, in getresponse
#     httplib_response = super().getresponse()
#                        ^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\http\client.py", line 1430, in getresponse
#     response.begin()
#   File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\http\client.py", line 331, in begin
#     version, status, reason = self._read_status()
#                               ^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\http\client.py", line 300, in _read_status
#     raise RemoteDisconnected("Remote end closed connection without"
# urllib3.exceptions.ProtocolError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
#
# During handling of the above exception, another exception occurred:
#
# Traceback (most recent call last):
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\ex1_1.py", line 22, in <module>
#     r=requests.get('https://httpstat.us/504'); print(r.status_code)
#       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\requests\api.py", line 87, in get
#     return request("get", url, params=params, **kwargs)
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\requests\api.py", line 71, in request
#     return session.request(method=method, url=url, **kwargs)
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\requests\sessions.py", line 651, in request
#     resp = self.send(prep, **send_kwargs)
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\requests\sessions.py", line 784, in send
#     r = adapter.send(request, **kwargs)
#         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\Administrator\Desktop\Self_learning\learning_stages\STAGE_01_HTTP_Basics\.venv\Lib\site-packages\requests\adapters.py", line 711, in send
#     raise ConnectionError(err, request=request)
# requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))