A very simple dependency resolution script.

Given configuration like this:
```yaml

---
mysql:
  deps: []
zookeeper:
  deps: []
kibana:
  deps:
    - mysql
fullhouse:
  deps:
    - kibana
    - zookeeper
```

Prints the order of start operations:
```
➜ python init.py start
Starting dependencies in order...
[mysql, zookeeper, kibana, fullhouse, init]
```

or stop operations:
```
➜ python init.py stop
Stopping dependencies in order...
[init, fullhouse, kibana, zookeeper, mysql]
```

`init` here represents root service, e.g. the beginning or operations (when we stop services) or the end (when we start them).
