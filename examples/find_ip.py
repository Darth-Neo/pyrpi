from netifaces import interfaces, ifaddresses, AF_INET

for ifaceName in interfaces():
    addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
    print '%s: %s' % (ifaceName, ', '.join(addresses))
