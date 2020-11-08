import argparse, logging, random, sys
import yaml

class Service:
    def __init__(self, name):
       self.name = name
       self.deps = []
 
    def addDependency(self, service):
       self.deps.append(service)

    def __repr__(self):
        return self.name

    def isolated(self):
        if self.deps:
            return False
        else:
            return True


def dep_resolve(service, resolved, visited):
    """
    A simple recursion to go over all edges of a given graph, which means calculating
    dependencies of root node
    """
    logger.debug(f"Starting resolution for {service}")
    visited.append(service)
    for dep in service.deps:
        if dep not in resolved:
            if dep in visited:
                sys.exit(f"Dependency loop detected: {service} -> {dep}")
            dep_resolve(dep, resolved, visited)
    resolved.append(service)

def _load_config(config):
    try:
        with open(config, 'r') as stream:
            config = yaml.safe_load(stream)
    except:
        sys.exit(f"Error opening {config}. Check that file exists and is a proper YAML")
    return config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calulate start/stop dependency order")
    parser.add_argument("action", choices=("start", "stop"))
    parser.add_argument("-c", "--config", default="services.yaml")
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()
    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    config = _load_config(args.config)

    # `init` is a root service, and all services in our config file are its dependencies
    init = Service('init')
    services = {'init': init}

    isolated = []

    # At first, we need to init list of our services. 
    # It is assumed to be complete, e.g. if dependency is not in services - error is shown
    for svc in config.keys():
        service = Service(svc)
        services[svc] = service
        init.addDependency(service)
    for svc, deps in config.items():
        service = services.get(svc)
        for dep in deps.get("deps"):
            dependency = services.get(dep, None)
            if dependency is None:
                sys.exit(f"Dependency {dep} is not present in list of services")
            dependency = services.get(dep)
            service.addDependency(dependency)
        if service.isolated():
            isolated.append(service)


               
    resolved = []
    dep_resolve(services.get("init"), resolved, [])
    s = set(isolated)
    others = [x for x in resolved if x not in s]

    if args.action == "start":
        logger.info("Starting in parallel")
        logger.info(isolated)
        logger.info("Starting in order...")
        logger.info(others)
    else:
        logger.info("Stopping dependencies in order...")
        logger.info(others[::-1])
        logger.info("Stopping in parallel:")
        logger.info(isolated)
