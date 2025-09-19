# BiQui
BiQui is a binary search algorithm based on queuing theory approximations
for V2N offloading and scaling. Using BiQui for scaling and offloading
results into minimizing objective functions as
 1. cost
 2. energy
 3. average delay

while meeting the e.g. 99.999 reliability constraint of V2N services.
That is, with BiQui you ensure that 99.999% of the times a vehicle
will experience V2N latencies below e.g. 100ms.


# Cite our work
You can cite either the IEEE TNSM or ACM MobiHoc versions of our work using the following BibTeX code:
```bibtex
@ARTICLE{biquitnsm,
  author={Chatzieleftheriou, Livia Elena and Jesúspérez-Valero and Martín-Pérez, Jorge and Serrano, Pablo},
  journal={IEEE Transactions on Network and Service Management}, 
  title={Optimal Scaling and Offloading for Sustainable Provision of Reliable V2N Services in Dynamic and Static Scenarios}, 
  year={2025},
  volume={},
  number={},
  pages={1-1},
  keywords={Ultra reliable low latency communication;Delays;Servers;Costs;Videos;Reliability;Vehicle dynamics;Computational modeling;Central Processing Unit;Artificial intelligence;Vehicle-to-Network;V2N;Ultra-reliable Low-Latency Communications;URLLC;Queueing Theory;Algorithm design;Optimization problem;Asymptotic optimality},
  doi={10.1109/TNSM.2025.3605408}}
```

```bibtex
@inproceedings{biquimobihoc,
author = {Chatzieleftheriou, Livia Elena and P\'{e}rez-Valero, Jes\'{u}s and Mart\'{\i}n-P\'{e}rez, Jorge and Serrano, Pablo},
title = {Sustainable Provision of URLLC Services for V2N: Analysis and Optimal Configuration},
year = {2024},
isbn = {9798400705212},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3641512.3686363},
doi = {10.1145/3641512.3686363},
abstract = {The rising popularity of Vehicle-to-Network (V2N) applications is driven by the Ultra-Reliable Low-Latency Communications (URLLC) service offered by 5G. The availability of distributed resources could be leveraged to handle the enormous traffic arising from these applications, but introduces complexity in deciding where to steer traffic under the stringent delay requirements of URLLC. In this paper, we introduce the V2N Computation Offloading and CPU Activation (V2N-COCA) problem, which aims at finding the computation offloading and the edge/cloud CPU activation decisions that minimize the operational costs, both monetary and energetic, under stringent latency constraints. Some challenges are the proven non-monotonicity of the objective function w.r.t. offloading decisions, and the no-existence of closed-formulas for the sojourn time of tasks. We present a provably tight approximation for the latter, and we design BiQui, a provably asymptotically optimal and with linear computational complexity w.r.t. computing resources algorithm for the V2N-COCA problem. We assess BiQui over real-world vehicular traffic traces, performing a sensitivity analysis and a stress-test. Results show that BiQui significantly outperforms state-of-the-art solutions, achieving optimal performance (found through exhaustive searches) in most of the scenarios.},
booktitle = {Proceedings of the Twenty-Fifth International Symposium on Theory, Algorithmic Foundations, and Protocol Design for Mobile Networks and Mobile Computing},
pages = {161–170},
numpages = {10},
keywords = {vehicle-to-network, V2N, ultra-reliable low-latency communications, URLLC, queueing theory, algorithm design, optimization problem, asymptotic optimality},
location = {Athens, Greece},
series = {MobiHoc '24}
}
```
