import requests 
  
API_ENDPOINT = "http://pastebin.com/api/api_post.php"

API_KEY = "XXXXXXXXXXXXXXXXX"
 
source_code = ''' 
print("Hello, world!") 
a = 1 
b = 2 
print(a + b) 
'''
  
data = {'api_dev_key':API_KEY, 
        'api_option':'paste', 
        'api_paste_code':source_code, 
        'api_paste_format':'python'} 
  
r = requests.post(url = API_ENDPOINT, data = data) 
  
res = r.text

print(res) 
