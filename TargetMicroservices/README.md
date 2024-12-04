# Microservices for AIOpsLab

## Overview
This repo is an extension and customization of the original [DeathStarBench](https://github.com/delimitrou/DeathStarBench) to suit specific fault injection purposes in microservice-based AIOps environments. This project includes additional features, modifications, and deletions to tailor the original work for improved usability and specific use cases.

## Features & Changes
- Enhanced deployment and support for functional fault injection.
    - Support for fault injection of MongoDb access control failure in the geo service of HoltelReservation.
    - Support for fault injection of MongoDb access control failure in the rate service of HoltelReservation.
    - Support for mitigation scripts of the above faults.
    - Feature of enabling TLS of MongoDB in SocialNetwork.
    - Introducing the source code bug to inject connection failure of rate service.
    - Modification of Dockerfile to build the SocialNetwork images.
- Removal of unnecessary files and directories for AIOpsLab.

## Attribution
This repo is based on [DeathStarBench](https://github.com/delimitrou/DeathStarBench), developed by the [SAIL group](http://sail.ece.cornell.edu/) at Cornell University, and licensed under the Apache License 2.0. The original code has been modified by Microsoft to include additional features and changes specific to AIOpsLab project. The Apache License 2.0 for the original project is included.

More details on the applications and a characterization of DeathStarBench can be found at ["An Open-Source Benchmark Suite for Microservices and Their Hardware-Software Implications for Cloud and Edge Systems"](http://www.csl.cornell.edu/~delimitrou/papers/2019.asplos.microservices.pdf), Y. Gan et al., ASPLOS 2019. 


## Code of Conduct

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.


## License

Copyright 2024 (c) Microsoft Corporation. All rights reserved.

Licensed under the [Apache](LICENSE) license.


<details>
  <summary>Original README</summary>

# DeathStarBench

Open-source benchmark suite for cloud microservices. DeathStarBench includes five end-to-end services, four for cloud systems, and one for cloud-edge systems running on drone swarms. 

## End-to-end Services

* Social Network (released)
* Media Service (released)
* Hotel Reservation (released)
* E-commerce site (in progress)
* Banking System (in progress)
* Drone coordination system (in progress)

## License & Copyright 

DeathStarBench is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 2.

DeathStarBench is being developed by the [SAIL group](http://sail.ece.cornell.edu/) at Cornell University. 

## Publications

More details on the applications and a characterization of their behavior can be found at ["An Open-Source Benchmark Suite for Microservices and Their Hardware-Software Implications for Cloud and Edge Systems"](http://www.csl.cornell.edu/~delimitrou/papers/2019.asplos.microservices.pdf), Y. Gan et al., ASPLOS 2019. 

If you use this benchmark suite in your work, we ask that you please cite the paper above. 


## Beta-testing

If you are interested in joining the beta-testing group for DeathStarBench, send us an email at: <microservices-bench-L@list.cornell.edu>