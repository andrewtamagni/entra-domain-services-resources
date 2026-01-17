# entra-domain-services-resources

This Pulumi template will deploy all the resources required to run AADDS in Azure, along with the associated management and networking resources.  It needs to run in a separate stack than the Core Enterprise stack.  It deploys a Spoke /24 VNET for AADDS management that is peered to the HUB VNET.  A separate VNET for the AADDS infrastructure that is peered to the AADDS management VNET is also deployed.  Network Security Groups and Route Tables are created that lock down traffic.  The AADDS VNET has LDAPS exposed to only on-prem and external eLibrary resources.  Traffic from the AADDS VNET can not be routed to the HUB network, only the AADDS management VNET.  The peering between the AADDS management VNET and AADDS VNET is left commented out initially with the Test VM.  The Peering must me initiated from the Core Enterprise stack first before it can be implemented on the AADDS stack.

---

## Third-Party Dependencies

This project uses the following third-party open-source libraries and tools:

- **Pulumi** (Apache-2.0 License) - Infrastructure as Code framework
- **Pulumi Azure Native** (Apache-2.0 License) - Azure provider for Pulumi
- **Pulumi Azure** (Apache-2.0 License) - Azure Classic provider for Pulumi

All dependencies are listed in `requirements.txt`. Please refer to each library's license for specific terms and conditions.