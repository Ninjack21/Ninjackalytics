state = 'dev'

if state != 'production':
    db_uri = 'postgres://nmuwkhjotaaskw:72d96dbc99aca32c929d466f77925a6141cfee480317847a16f4a5dc35e765d7@ec2-34-233-115-14.compute-1.amazonaws.com:5432/dd1vv602smkivi'
else:
    db_uri = 'postgres://hkevcdgapzwbgq:e4f06a129ac6687738bfb3140272e45c405746bda075681a05595a186ae84013@ec2-52-72-56-59.compute-1.amazonaws.com:5432/d1vgs7fthk106f'
