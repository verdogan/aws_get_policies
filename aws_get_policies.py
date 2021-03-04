import boto3
import requests


client = boto3.client('lambda')
response = client.list_functions()

func_kwargs = dict(MaxItems=10000)
functions_names_returned = dict()
while True:
    response = client.list_functions(**func_kwargs)
    functions_info = response['Functions']
    all_functions_names = {x['FunctionName']:x['Role'] for x in functions_info}
    functions_names_returned = {**all_functions_names, **functions_names_returned}
    marker = response.get('NextMarker')
    if not marker:
        break
    func_kwargs['Marker'] = marker

functions_names_returned = list(set(functions_names_returned.values()))
functions_names_returned = sorted(functions_names_returned)
service_roles = [name for name in functions_names_returned if str.startswith(name, 'arn:aws:iam::462037219736:role/service-role/')]
service_roles = [role.split('/')[-1] for role in service_roles]

policies_list = []
for value in functions_names_returned:
    try:
        role_name = value.split('/')[-1]
        client = boto3.resource('iam')
        role = client.Role(role_name)
        attached_policies = list(role.attached_policies.all())
        policies_list.extend(attached_policies)
    except:
        continue
policies_list = list(set(policies_list))

for policy in policies_list:
    if policy.arn.startswith('arn:aws:iam::aws'):
        print(policy.default_version.document)
