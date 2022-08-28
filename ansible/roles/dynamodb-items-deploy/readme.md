# AWS DynamoDB Table - Data Load Items

## Features
Deploy DynamoDB - data load items into table

## Prereq's

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install require packages.

```bash
python3 -m venv .ve
source .ve/bin/activate
pip3 install -r requirements.txt 1>/dev/null
```

## Usage

```python
python3 dynamodb-items-deploy.py {{ file_name }}.json
```

## json file example
```json
{
   "table1":[
      {
         "_id": "table1-item1",
         "index": 0,
         "guid": "8cba24c8-4ead-46c9-858d-4d96c0e6a6c3",
         "isActive": true,
         "balance": "$2,783.83",
         "picture": "http://placehold.it/32x32",
         "age": 22,
         "eyeColor": "brown",
         "name": "Trisha Foster",
         "languages":[
            "English",
            "German"
         ]
      },
      {
         "_id": "table1-item2",
         "index": 1,
         "guid": "88ac03dc-e699-4c44-a1c8-4d822e6ecd92",
         "isActive": false,
         "balance": "$1,715.42",
         "picture": "http://placehold.it/32x32",
         "age": 24,
         "eyeColor": "brown",
         "name": "Calhoun Marks",
         "gender": "male",
         "company": "PASTURIA",
         "languages":[
            "English"
         ]
      }
   ],
   "table2":[
      {
         "_id": "table2-item1",
         "index": 2,
         "guid": "95f3c3d9-d194-4123-80c9-a2aa7d982acf",
         "isActive": true,
         "balance": "$1,435.68",
         "picture": "http://placehold.it/32x32",
         "age": 34,
         "eyeColor": "green",
         "name": "Solis Cortez",
         "gender": "male",
         "company": "GORGANIC"
      }
   ],
   "table3":[
      {
         "_id": "table3-item1",
         "index": 4,
         "guid": "b9bf8594-1067-4e8a-8b34-a8321ea60657",
         "isActive": false,
         "balance": "$1,290.77",
         "picture": "http://placehold.it/32x32",
         "age": 27,
         "eyeColor": "brown",
         "name": "Jacqueline Johnston",
         "gender": "female",
         "company": "ISOPLEX",
         "friends": [
            {
              "id": 0,
              "name": "Whitley Bonner"
            },
            {
              "id": 1,
              "name": "Cynthia Vance"
            },
            {
              "id": 2,
              "name": "Tabitha Jacobs"
            }
          ]
      },
      {
         "_id": "table3-item2",
         "index": 5,
         "guid": "3d9c1d64-0782-4d1f-804a-82b690320bec",
         "isActive": false,
         "balance": "$1,181.06",
         "picture": "http://placehold.it/32x32",
         "age": 30,
         "eyeColor": "green",
         "name": "Britney Nash",
         "gender": "female",
         "company": "ZIDANT",
         "tags": [
            "non",
            "magna",
            "commodo",
            "cupidatat",
            "duis",
            "sunt",
            "ex"
          ]
      }
   ]
}
```

## How to run playbook
```
ansible-playbook playbooks/dynamodb-items-deploy.yml -e branch=master -e env=dev1 -e region=us-east-2 -e git_project=DevOps-RV -e git_repo=aws -e file_name=<path to json file in repo>
```

### Author
_Raghu Vamsi_

#### 🔗 Links
[![Linkedin](https://img.shields.io/badge/-LinkedIn-blue?style=flat&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/devops-rv/)](https://www.linkedin.com/in/devops-rv/)
[![Medium](https://img.shields.io/badge/-Medium-000000?style=flat&labelColor=000000&logo=Medium&link=https://medium.com/@DevOps-Rv)](https://medium.com/@DevOps-Rv)