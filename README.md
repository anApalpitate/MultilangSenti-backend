## 项目结构

```shell
/src
├── api
│   ├── __init__.py
│   ├── auth.py
│   └── file.py
├── config.py
├── database
│   ├── __init__.py
│   ├── fileOperation.py
│   ├── session.py
│   └── userOperation.py
├── main.py
├── model
│   ├── __init__.py
│   ├── user.py
│   └── userFile.py
├── resources
│   ├── data.db
├── service
│   └── __init__.py
├── test
│   ├── files
│   │   ├── file1.txt
│   │   ├── file2.jpg
│   │   ├── file3.pdf
│   │   ├── file4.png
│   │   └── file5.md
│   ├── test_auth.py
│   └── test_file.py
└── util
    ├── FileTree.py
    ├── __init__.py
    ├── authUtil.py
    └── log.py
```