# Authorization
[Docs](https://developers.pinterest.com/docs/getting-started/authentication/)

1. Generating an access token
```
https://www.pinterest.com/oauth/?client_id=1484092&redirect_uri=https://web.kosyachniy.com/pinterest&response_type=code&scope=boards:read,boards:write,pins:read,pins:write,user_accounts:read,catalogs:read,catalogs:write&state=123
```

code ``


2. Generate token
```
echo -n 0000000:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx | base64
```

token ``


3.
```
curl -X POST https://api.pinterest.com/v5/oauth/token
--header 'Authorization: Basic ...'
--header 'Content-Type: application/x-www-form-urlencoded'
--data-urlencode 'grant_type=authorization_code'
--data-urlencode 'code=...'
--data-urlencode 'redirect_uri=https://web.kosyachniy.com/pinterest'
```


4. Create board
```
curl --location --request POST 'https://api.pinterest.com/v5/boards' \
--header 'Authorization: Bearer <Add your token here>' \
--header 'Content-Type: application/json' \
--data-raw '{
      "name": "Summer Recipes",
      "description": "My favorite summer recipes",
      "privacy": "PUBLIC"
}'
```


5. List
curl --location --request GET 'https://api.pinterest.com/v5/boards' \
--header 'Authorization: Bearer pina_...' \
--header 'Content-Type: application/json'

```
{"items":[{"privacy":"PUBLIC","id":"1063553336940651725","owner":{"username":"chilleco"},"name":"HotDealUp","description":""},{"privacy":"PUBLIC","id":"1063553336940685346","owner":{"username":"chilleco"},"name":"Summer Recipes","description":"My favorite summer recipes"}],"bookmark":null}%
```

board ``




6. Create pin
```
curl --location --request POST 'https://api-sandbox.pinterest.com/v5/pins' \
--header 'Authorization: Bearer pina_...' \
--header 'Content-Type: application/json' \
--data-raw '{
      "title": "Platye",
      "description": "Krytoe platye",
      "board_id": "1063553336940651725",
      "media_source": {
        "source_type": "image_url",
        "url": "https://slimages.macysassets.com/is/image/MCY/products/6/optimized/23504216_fpx.tif?op_sharpen=1&wid=560&fit=fit,1&$filtersm$"
      }
  }'
```


```
curl --request DELETE 'https://api-sandbox.pinterest.com/v5/pins/<insert_sandbox_pin_id>/save' \
--header 'Authorization: Bearer <Add your token here>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "board_id": <insert_new_sandbox_board_id>
}'
```




post('1063553336940651725', 'https://images.asos-media.com/products/asos-design-oversized-hoodie-in-black-with-multi-placement-graphics-part-of-a-set/200544807-1-black?$n_550w$&wid=550&fit=constrain', '123', '*456*\n**789**<br>***123***<br />qwe\trty\n\nzxc')





https://developers.pinterest.com/apps/1484092/



https://developers.pinterest.com/docs/api/v5/#operation/pins/create


https://github.com/pinterest/pinterest-python-sdk

