vpcs = ["main", "database"]

new_vpcs = []
for name in vpcs:
    new_vpcs.append(name.title())

print(new_vpcs)

new_v2_vpcs = [vpc.title() for vpc in vpcs]

print(new_v2_vpcs)

new_v3_vpcs = [vpc.title() for vpc in vpcs if len(vpc) < 5]

print(new_v3_vpcs)
