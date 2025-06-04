## Test Models
```bash
cd backend/ctfd/plugin
python -m pytest tests/test_working_models.py -v
```

## Generate Seed Data
First start CTFd to create tables, then add seed data:

```bash
npm start
npm stop
cd external/CTFd
flask shell
>>> exec(open('../../backend/ctfd/plugin/seed_data.py').read())
>>> demo_seed()
>>> exit()
```
