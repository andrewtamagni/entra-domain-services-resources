"""An Azure RM Python Pulumi program"""

import pulumi
import ipaddress
from pulumi_azure_native import resources
import pulumi_azure as azure_classic
import pulumi_azure_native as azure_native
from default_vars import rg_prefix,aadds_name,pfx_cert_string,pfx_pw,aadds_vnet_space,aadds_dns_servers,OnPrem_SourceIpRange,ldap_source_1,ldap_source_3,ldap_source_2,hub_vnet_resource_id,hub_vnet_space,trust_priv_ip,ms01_vm_name,ms01_admin_username,ms01_admin_pw,ldap_source_4,ldap_source_5#,testvm01_vm_name,testvm01_admin_username,testvm01_admin_pw

#Generate VNET and Subnet address spaces from a /24 CIDR for the AADDS Spoke.
subnets_25 = list(ipaddress.ip_network(aadds_vnet_space).subnets(new_prefix=25)) # /25 Subnets within VNET Address Space
subnets_26 = list(ipaddress.ip_network(aadds_vnet_space).subnets(new_prefix=26)) # /26 Subnets within VNET Address Space
aadds_ms_vnet = str(subnets_25[0])          # First /25
aadds_ms_subnet1_space = str(subnets_26[0]) # First /26
aadds_ms_subnet2_space = str(subnets_26[1]) # Second /26
aadds_vnet = str(subnets_25[1])             # Second /25
aadds_subnet1_space = str(subnets_26[2])    # Third /26
aadds_subnet2_space = str(subnets_26[3])    # Fourth /26

########## Resources ##########

aadds_resource_group = resources.ResourceGroup(str(rg_prefix) + "-Infrastructure",
    resource_group_name=str(rg_prefix) + "-Infrastructure",
)

aadds_ms_networking_resource_group = resources.ResourceGroup(str(rg_prefix) + "-MS-Networking",
    resource_group_name=str(rg_prefix) + "-MS-Networking",
)

aadds_networking_resource_group = resources.ResourceGroup(str(rg_prefix) + "-Networking",
    resource_group_name=str(rg_prefix) + "-Networking",
)

aadds_ms_vm_resource_group = resources.ResourceGroup(str(rg_prefix) + "-" + str(ms01_vm_name) + "-VM",
    resource_group_name=str(rg_prefix) + "-" + str(ms01_vm_name) + "-VM",
)

# AADDS MS VNET and Subnets
aadds_ms_virtual_network = azure_classic.network.VirtualNetwork(str(rg_prefix) + "-MS-VNET",
    opts=pulumi.ResourceOptions(depends_on=[aadds_ms_networking_resource_group]),
    name=str(rg_prefix) + "-MS-VNET",
    location=aadds_ms_networking_resource_group.location,
    resource_group_name=aadds_ms_networking_resource_group.name,
    address_spaces=[aadds_ms_vnet],
    dns_servers=aadds_dns_servers,
)

aadds_ms_subnet1 = azure_classic.network.Subnet(str(rg_prefix) + "-MS-VNET-1",
    opts=pulumi.ResourceOptions(depends_on=[aadds_ms_virtual_network]),
    name=str(rg_prefix) + "-MS-VNET-1",
    resource_group_name=aadds_ms_networking_resource_group.name,
    virtual_network_name=aadds_ms_virtual_network.name,
    address_prefixes=[aadds_ms_subnet1_space],
)

aadds_ms_subnet2 = azure_classic.network.Subnet(str(rg_prefix) + "-MS-VNET-2",
    opts=pulumi.ResourceOptions(depends_on=[aadds_ms_virtual_network]),
    name=str(rg_prefix) + "-MS-VNET-2",
    resource_group_name=aadds_ms_networking_resource_group.name,
    virtual_network_name=aadds_ms_virtual_network.name,
    address_prefixes=[aadds_ms_subnet2_space],
)

# AADDS DC VNET and Subnets
aadds_virtual_network = azure_classic.network.VirtualNetwork(str(rg_prefix) + "-VNET",
    opts=pulumi.ResourceOptions(depends_on=[aadds_networking_resource_group]),
    name=str(rg_prefix) + "-VNET",
    location=aadds_networking_resource_group.location,
    resource_group_name=aadds_networking_resource_group.name,
    address_spaces=[aadds_vnet],
    dns_servers=aadds_dns_servers,
)

aadds_subnet1 = azure_classic.network.Subnet(str(rg_prefix) + "-VNET-1",
    opts=pulumi.ResourceOptions(depends_on=[aadds_virtual_network]),
    name=str(rg_prefix) + "-VNET-1",
    resource_group_name=aadds_networking_resource_group.name,
    virtual_network_name=aadds_virtual_network.name,
    address_prefixes=[aadds_subnet1_space],
)

aadds_subnet2 = azure_classic.network.Subnet(str(rg_prefix) + "-VNET-2",
    opts=pulumi.ResourceOptions(depends_on=[aadds_virtual_network]),
    name=str(rg_prefix) + "-VNET-2",
    resource_group_name=aadds_networking_resource_group.name,
    virtual_network_name=aadds_virtual_network.name,
    address_prefixes=[aadds_subnet2_space],
)

# AADDS MS VNET Network Security Group
aadds_ms_network_security_group = azure_classic.network.NetworkSecurityGroup(str(rg_prefix) + "-MS-NSG",
opts=pulumi.ResourceOptions(depends_on=[aadds_ms_networking_resource_group]),
name=str(rg_prefix) + "-MS-NSG",
    location=aadds_ms_networking_resource_group.location,
    resource_group_name=aadds_ms_networking_resource_group.name,
    security_rules=[azure_classic.network.NetworkSecurityGroupSecurityRuleArgs(
        name="Allow-RDP-CorpNetSaw",
        protocol="TCP",
        source_port_range="*",
        destination_port_range="3389",
        source_address_prefix="CorpNetSaw",
        destination_address_prefix="*",
        access="Allow",
        priority=201,
        direction="Inbound",
        ),
        azure_classic.network.NetworkSecurityGroupSecurityRuleArgs(
        name="Allow-RDP-Org",
        protocol="TCP",
        source_port_range="*",
        destination_port_range="3389",
        source_address_prefix=OnPrem_SourceIpRange,
        destination_address_prefix="*",
        access="Allow",
        priority=211,
        direction="Inbound",
        ),
    ],
)

aadds_ms_network_security_group_association = azure_classic.network.SubnetNetworkSecurityGroupAssociation(str(rg_prefix) + "-MS-NSG-Association",
    opts=pulumi.ResourceOptions(depends_on=[aadds_ms_network_security_group,aadds_ms_subnet1]),
    subnet_id=aadds_ms_subnet1.id,
    network_security_group_id=aadds_ms_network_security_group.id,
)

# AADDS DC VNET Network Security Group
aadds_network_security_group = azure_classic.network.NetworkSecurityGroup(str(rg_prefix) + "-NSG",
opts=pulumi.ResourceOptions(depends_on=[aadds_networking_resource_group]),
name=str(rg_prefix) + "-NSG",
    location=aadds_networking_resource_group.location,
    resource_group_name=aadds_networking_resource_group.name,
    security_rules=[azure_classic.network.NetworkSecurityGroupSecurityRuleArgs(
        name="Allow-LDAPS-Inbound-From-IP_Org",
        protocol="TCP",
        source_port_range="*",
        destination_port_range="636",
        source_address_prefix=OnPrem_SourceIpRange,
        destination_address_prefix="*",
        access="Allow",
        priority=311,
        direction="Inbound",
        ),
        azure_classic.network.NetworkSecurityGroupSecurityRuleArgs(
        name="Allow-LDAPS-Inbound-From-IP_1",
        protocol="TCP",
        source_port_range="*",
        destination_port_range="636",
        source_address_prefix=ldap_source_1,
        destination_address_prefix="*",
        access="Allow",
        priority=312,
        direction="Inbound",
        ),
        azure_classic.network.NetworkSecurityGroupSecurityRuleArgs(
        name="Allow-LDAPS-Inbound-From-IP_2",
        protocol="TCP",
        source_port_range="*",
        destination_port_range="636",
        source_address_prefix=ldap_source_2,
        destination_address_prefix="*",
        access="Allow",
        priority=313,
        direction="Inbound",
        ),
        azure_classic.network.NetworkSecurityGroupSecurityRuleArgs(
        name="Allow-LDAPS-Inbound-From-IP_3",
        protocol="TCP",
        source_port_range="*",
        destination_port_range="636",
        source_address_prefix=ldap_source_3,
        destination_address_prefix="*",
        access="Allow",
        priority=314,
        direction="Inbound",
        ),
        azure_classic.network.NetworkSecurityGroupSecurityRuleArgs(
        name="Allow-LDAPS-Inbound-From-IP_4",
        protocol="TCP",
        source_port_range="*",
        destination_port_range="636",
        source_address_prefix=ldap_source_4,
        destination_address_prefix="*",
        access="Allow",
        priority=315,
        direction="Inbound",
        ),
        azure_classic.network.NetworkSecurityGroupSecurityRuleArgs(
        name="Allow-LDAPS-Inbound-From-IP_5",
        protocol="TCP",
        source_port_range="*",
        destination_port_range="636",
        source_address_prefix=ldap_source_5,
        destination_address_prefix="*",
        access="Allow",
        priority=316,
        direction="Inbound",
        ),
        azure_classic.network.NetworkSecurityGroupSecurityRuleArgs(
        name="Allow-PS-Remoting",
        protocol="TCP",
        source_port_range="*",
        destination_port_range="5986",
        source_address_prefix="AzureActiveDirectoryDomainServices",
        destination_address_prefix="*",
        access="Allow",
        priority=301,
        direction="Inbound",
        ),        
    ]
)

aadds_network_security_group_association = azure_classic.network.SubnetNetworkSecurityGroupAssociation(str(rg_prefix) + "-NSG-Association",
    opts=pulumi.ResourceOptions(depends_on=[aadds_network_security_group,aadds_subnet1]),
    network_security_group_id=aadds_network_security_group.id,
    subnet_id=aadds_subnet1.id,
)

# AADDS Instance
domain_service = azure_native.aad.DomainService(str(aadds_name),
    opts=pulumi.ResourceOptions(depends_on=[aadds_resource_group,aadds_subnet1]),
    resource_group_name=aadds_resource_group.name,
    domain_name=aadds_name,
    domain_service_name=aadds_name,
    replica_sets=[azure_native.aad.ReplicaSetArgs(
        subnet_id=aadds_subnet1.id,
    )],
    ldaps_settings=azure_native.aad.LdapsSettingsArgs(
        external_access="Enabled",
        ldaps="Enabled",
        pfx_certificate=pfx_cert_string,
        pfx_certificate_password=pfx_pw,
    ),
    domain_security_settings=azure_native.aad.DomainSecuritySettingsArgs(
        tls_v1="Disabled",
        ntlm_v1="Enabled",
        sync_ntlm_passwords="Enabled",        
        sync_on_prem_passwords="Enabled",
        kerberos_rc4_encryption="Enabled",
        kerberos_armoring="Enabled",        
    ),
    filtered_sync="Disabled",
    domain_configuration_type="FullySynced",    
    notification_settings=azure_native.aad.NotificationSettingsArgs(
        notify_dc_admins="Enabled",
        notify_global_admins="Enabled",
    ),    
    sku="Standard",
)

# Management Server 01 Network Interface
ms01_network_interface = azure_classic.network.NetworkInterface(str(ms01_vm_name) + "-eth0",
    opts=pulumi.ResourceOptions(depends_on=[aadds_ms_subnet1]),
    name=str(ms01_vm_name) + "-eth0",
    location=aadds_ms_vm_resource_group.location,
    resource_group_name=aadds_ms_vm_resource_group.name,
    ip_configurations=[azure_classic.network.NetworkInterfaceIpConfigurationArgs(
        name="ipconfig-mgmt",
        primary=True,
        subnet_id=aadds_ms_subnet1.id,
        private_ip_address_allocation="Dynamic",
        private_ip_address_version="IPv4")],        
    enable_accelerated_networking=True,
    enable_ip_forwarding=True,
)

# Management Server 01 VM
ms01_virtual_machine = azure_classic.compute.VirtualMachine(str(ms01_vm_name),
    opts=pulumi.ResourceOptions(depends_on=[ms01_network_interface]),
    name=str(ms01_vm_name),
    location=aadds_ms_vm_resource_group.location,
    resource_group_name=aadds_ms_vm_resource_group.name,
    network_interface_ids=[ms01_network_interface],
    primary_network_interface_id=ms01_network_interface,
    vm_size="Standard_D2s_v3",
    storage_image_reference=azure_classic.compute.VirtualMachineStorageImageReferenceArgs(
        publisher="MicrosoftWindowsServer",
        offer="WindowsServer",
        sku="2022-datacenter-azure-edition",
        version="latest",
    ),
    storage_os_disk=azure_classic.compute.VirtualMachineStorageOsDiskArgs(
        name=str(ms01_vm_name) + "_OsDisk_1",
        caching="ReadWrite",
        create_option="FromImage",
        managed_disk_type="StandardSSD_LRS",
        disk_size_gb=127,
        os_type = "Windows",
    ),
    os_profile=azure_classic.compute.VirtualMachineOsProfileArgs(
        computer_name=str(ms01_vm_name),
        admin_username=str(ms01_admin_username),
        admin_password=str(ms01_admin_pw),
    ),
    os_profile_windows_config=azure_classic.compute.VirtualMachineOsProfileWindowsConfigArgs(
        provision_vm_agent=True,
        enable_automatic_upgrades=False,

    ),
    license_type="Windows_Server",
)

# AADDS MS VNET Route Table
aadds_ms_route_table = azure_native.network.RouteTable(str(rg_prefix) + "-MS-VNET-to-FW",
    opts=pulumi.ResourceOptions(depends_on=[aadds_ms_subnet1,aadds_subnet1]),
    route_table_name=str(rg_prefix) + "-MS-VNET-to-FW",
    location=aadds_ms_networking_resource_group.location,
    resource_group_name=aadds_ms_networking_resource_group.name,
    disable_bgp_route_propagation=False,
    routes=[
        azure_native.network.RouteArgs(name=str(rg_prefix) + "-MS-VNET-to-FW_Route1",
        address_prefix="0.0.0.0/0",
        next_hop_type="VirtualAppliance",
        next_hop_ip_address=trust_priv_ip),
        
        azure_native.network.RouteArgs(name=str(rg_prefix) + "-MS-VNET-to-FW_Route2",
        address_prefix=OnPrem_SourceIpRange,
        next_hop_type="VirtualNetworkGateway"),

        azure_native.network.RouteArgs(name=str(rg_prefix) + "-MS-VNET-to-FW_Route3",
        address_prefix="192.168.0.0/16",
        next_hop_type="VirtualNetworkGateway"),

        azure_native.network.RouteArgs(name=str(rg_prefix) + "-MS-VNET-to-FW_Route4",
        address_prefix="172.16.0.0/12",
        next_hop_type="VirtualNetworkGateway"),

        azure_native.network.RouteArgs(name=str(rg_prefix) + "-MS-VNET-to-FW_Route5",
        address_prefix="10.0.0.0/8",
        next_hop_type="VirtualAppliance",
        next_hop_ip_address=trust_priv_ip),

        azure_native.network.RouteArgs(name=str(rg_prefix) + "-MS-VNET-to-FW_Route6",
        address_prefix=hub_vnet_space,
        next_hop_type="VirtualAppliance",
        next_hop_ip_address=trust_priv_ip),
    ])

# Associate AADDS MS Route Table
aadds_ms_route_table_association_subnet1 = azure_classic.network.SubnetRouteTableAssociation(str(rg_prefix) + "-MS-VNET-to-FW-Association",
    opts=pulumi.ResourceOptions(depends_on=[aadds_ms_route_table]),
    subnet_id=aadds_ms_subnet1.id,
    route_table_id=aadds_ms_route_table.id)

# Create AADDS-MS-VNET-to-HUB Peering
hub_vnet_virtual_network_peering = azure_native.network.VirtualNetworkPeering(str(rg_prefix) + "-MS-VNET-to-HUB",
    opts=pulumi.ResourceOptions(depends_on=[aadds_ms_virtual_network]),
    virtual_network_peering_name=str(rg_prefix) + "-MS-VNET-to-HUB",
    allow_forwarded_traffic=True,
    allow_gateway_transit=False,
    allow_virtual_network_access=True,
    remote_virtual_network=azure_native.network.SubResourceArgs(
        id=hub_vnet_resource_id,
    ),
    resource_group_name=aadds_ms_networking_resource_group.name,
    use_remote_gateways=True,
    virtual_network_name=aadds_ms_virtual_network.name,
)

# Create AADDS-MS-VNET-to-AADDS-VNET Peering
aadds_ms_vnet_virtual_network_peering = azure_native.network.VirtualNetworkPeering(str(rg_prefix) + "-MS-VNET-to-AADDS-VNET",
    opts=pulumi.ResourceOptions(depends_on=[aadds_ms_virtual_network,aadds_virtual_network]),
    virtual_network_peering_name=str(rg_prefix) + "-MS-VNET-to-AADDS-VNET",
    allow_forwarded_traffic=True,
    allow_gateway_transit=False,
    allow_virtual_network_access=True,
    remote_virtual_network=azure_native.network.SubResourceArgs(
        id=aadds_virtual_network.id,
    ),
    resource_group_name=aadds_ms_networking_resource_group.name,
    use_remote_gateways=False,
    virtual_network_name=aadds_ms_virtual_network.name,
)

# Create AADDS-VNET-to-AADDS-MS-VNET Peering
aadds_vnet_virtual_network_peering = azure_native.network.VirtualNetworkPeering(str(rg_prefix) + "-VNET-to-AADDS-MS-VNET",
    opts=pulumi.ResourceOptions(depends_on=[aadds_ms_virtual_network,aadds_virtual_network]),
    virtual_network_peering_name=str(rg_prefix) + "-VNET-to-AADDS-MS-VNET",
    allow_forwarded_traffic=True,
    allow_gateway_transit=False,
    allow_virtual_network_access=True,
    remote_virtual_network=azure_native.network.SubResourceArgs(
        id=aadds_ms_virtual_network.id,
    ),
    resource_group_name=aadds_networking_resource_group.name,
    use_remote_gateways=False,
    virtual_network_name=aadds_virtual_network.name,
)    

##### For Testing #####
"""
#TEST VM 01 RG
testvm01_resource_group = resources.ResourceGroup(str(rg_prefix) + "-" + str(testvm01_vm_name) + "-VM",
    resource_group_name=str(rg_prefix) + "-" + str(testvm01_vm_name) + "-VM"
)

# TEST VM 01 Network Interface
testvm01_network_interface = azure_classic.network.NetworkInterface(str(testvm01_vm_name) + "-eth0",
    opts=pulumi.ResourceOptions(depends_on=[aadds_subnet1,testvm01_resource_group,domain_service]),
    name=str(testvm01_vm_name) + "-eth0",
    location=testvm01_resource_group.location,
    resource_group_name=testvm01_resource_group.name,
    ip_configurations=[azure_classic.network.NetworkInterfaceIpConfigurationArgs(
        name="ipconfig-mgmt",
        primary=True,
        subnet_id=aadds_subnet1.id,
        private_ip_address_allocation="Dynamic",
        private_ip_address_version="IPv4")],        
    enable_accelerated_networking=False,
    enable_ip_forwarding=True,
)

# TEST VM 01
testvm01_virtual_machine = azure_classic.compute.VirtualMachine(str(testvm01_vm_name),
    opts=pulumi.ResourceOptions(depends_on=[testvm01_network_interface]),
    name=str(testvm01_vm_name),
    location=testvm01_resource_group.location,
    resource_group_name=testvm01_resource_group.name,
    network_interface_ids=[testvm01_network_interface],
    primary_network_interface_id=testvm01_network_interface,
    vm_size="Standard_B2ms",
    storage_image_reference=azure_classic.compute.VirtualMachineStorageImageReferenceArgs(
        publisher="microsoftwindowsdesktop",
        offer="windows-ent-cpc",
        sku="win11-21h2-ent-cpc-m365",
        version="latest",
    ),
    storage_os_disk=azure_classic.compute.VirtualMachineStorageOsDiskArgs(
        name=str(testvm01_vm_name) + "_OsDisk_1",
        caching="ReadWrite",
        create_option="FromImage",
        managed_disk_type="Standard_LRS",
        os_type = "Windows",
    ),
    os_profile=azure_classic.compute.VirtualMachineOsProfileArgs(
        computer_name=str(testvm01_vm_name),
        admin_username=str(testvm01_admin_username),
        admin_password=str(testvm01_admin_pw),
    ),
    os_profile_windows_config=azure_classic.compute.VirtualMachineOsProfileWindowsConfigArgs(
        provision_vm_agent=True,
        enable_automatic_upgrades=False,

    ),
    license_type="Windows_Client",
)
"""
pulumi.export("AADDS Domain Name", aadds_name)
pulumi.export(str(rg_prefix) + "-MS-VNET", aadds_ms_vnet)
pulumi.export(str(rg_prefix) + "-MS-1", aadds_ms_subnet1_space)
pulumi.export(str(rg_prefix) + "-MS-2", aadds_ms_subnet2_space)
pulumi.export(str(rg_prefix) + "-VNET", aadds_vnet)
pulumi.export(str(rg_prefix) + "-1", aadds_subnet1_space)
pulumi.export(str(rg_prefix) + "-2", aadds_subnet2_space)
pulumi.export("Management Server 01 VM Name", ms01_vm_name)
pulumi.export("Management Server Private IP", ms01_network_interface.private_ip_address)

# For Testing
#pulumi.export("TEST VM 01 Name", testvm01_vm_name)
#pulumi.export("TEST VM 01 Private IP", testvm01_network_interface.private_ip_address)