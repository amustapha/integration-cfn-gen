from typing import Iterable, Union

from troposphere import AWSObject, Output, Export, Parameter, Tags
from troposphere import GetAtt, Ref, Sub, Split, ImportValue, Select
from troposphere import ec2

from .common import Config

VPC = ImportValue(Sub('${Stage}-VPC'))
PUBLIC_SUBNETS = Split(',', ImportValue(Sub('${Stage}-PublicSubnets')))
PRIVATE_SUBNETS = Split(',', ImportValue(Sub('${Stage}-PrivateSubnets')))


def items(config: Config) -> Iterable[Union[AWSObject, Parameter, Output]]:
    if not config.NAT_GATEWAY:
        return

    yield Parameter('NatSubnetCidr',
                    Type='String',
                    Description='CIDR for subnet, e.g. 10.11.12.0/24')

    yield ec2.SecurityGroup('NatSecurityGroup',
                            GroupDescription='Egress Only',
                            VpcId=VPC)

    elastic_ip = ec2.EIP('NatElasticIp',
                         Domain='vpc')
    yield elastic_ip

    nat = ec2.NatGateway('NatNat',
                         AllocationId=GetAtt(elastic_ip, 'AllocationId'),
                         SubnetId=Select(1, PUBLIC_SUBNETS))
    yield nat

    privsubnet = ec2.Subnet('NatPrivSubnet',
                            CidrBlock=Ref('NatSubnetCidr'),
                            MapPublicIpOnLaunch=False,
                            VpcId=VPC,
                            Tags=Tags(
                                Name=Sub('${AWS::StackName} NAT Priv Subnet')
                            ))
    yield privsubnet

    private_route_table = ec2.RouteTable('NatPrivRouteTable', VpcId=VPC)
    yield private_route_table
    yield ec2.Route('NatRoute',
                    RouteTableId=Ref(private_route_table),
                    DestinationCidrBlock='0.0.0.0/0',
                    NatGatewayId=Ref(nat))
    yield ec2.SubnetRouteTableAssociation(
        'NatPrivRouteTableAssn',
        RouteTableId=Ref(private_route_table),
        SubnetId=Ref(privsubnet))

    yield Output('NatElasticIp',
                 Value=Ref(elastic_ip),
                 Description='NAT Elastic IP Address',
                 Export=Export(Sub('${AWS::StackName}-NatElasticIp')))
