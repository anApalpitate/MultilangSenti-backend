## 项目结构

```shell
/backend
├── .gitignore
├── README.md
├── docs
│   ├── 前端设计文档.md
│   ├── 接口文档.md
│   ├── 流程文档.md
│   └── 需求文档.md
├── requirements.txt
└── src
    ├── api
    │   ├── __init__.py
    │   └── auth.py
    ├── config.py
    ├── database
    │   ├── __init__.py
    │   ├── session.py
    │   └── userOperation.py
    ├── main.py
    ├── model
    │   ├── __init__.py
    │   └── user.py
    ├── resources
    │   ├── data.db
    │   └── filetree.txt
    ├── service
    │   └── __init__.py
    ├── test
    │   ├── .pytest_cache
    │   │   ├── .gitignore
    │   │   ├── CACHEDIR.TAG
    │   │   ├── README.md
    │   │   └── v
    │   │       └── cache
    │   │           ├── lastfailed
    │   │           └── nodeids
    │   └── test_auth.py
    └── util
        ├── FileTree.py
        ├── __init__.py
        ├── authUtil.py
        └── log.py
```