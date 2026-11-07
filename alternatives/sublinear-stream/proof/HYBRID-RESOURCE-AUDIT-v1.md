# 混合构造的实测口径审计

本次实际exit0：480 cases，4448逐feed对照，2915 RNG状态检查，1763 native-prefix检查，355次重建和12664个重建时Read验证。小H(0/1/3/6/16)、两正常toy profile、prompt/feedback、恰H、guard、EOS均覆盖有限sanity，不替代全域证明。

## 资源结果不能挑好看的讲

长例使用H=16，p=134时两个正常profile的full后端仍占31968数值槽，原KV1072。迁移边界保留原生128 word与新表19980槽，cache组件重叠20108。后续31968是该例更大组件峰值。这个小H只是功能测试，根本没有达到cache竞争条件。

若H覆盖整个run，按算法不会创建森林；这是固定H命题，不用本次H16长例冒充已测大H范围，也不是整个设备零额外开销。

## 组件竞争控制与区间证书

对R(t)=8t、S(t)=K bit_length(t+1)，dyadic证书给永久交叉点：

- K3996：6494；K752：1034；K776：1067；K16：8。

后继区间的左端关系为a*lo_next=2a*lo+a，保证首个全满足区间后的所有区间也满足，不把有限扫描叫永久证明。

只在zero-key结构控制中，特化K16/H8满足迁移cache组件≤2×原KV峰值；682次组件检查通过。它不是人类baseline，不把其资源优势外推到两个正常profile或实际200B。

## 未计组件与测试observer

cache数值槽外还有重建scratch、readonly code/权重/证书、容器/控制/RNG、诊断堆栈等。full模式metadata_serialized_bytes=0仅指未创建pruned证书JSON对象，不代表完整程序/模型没有readonly成本。

构造中的全query Read比较是诊断，只验证已建cache，不把参考答案写回状态；默认生产stream不带observer，debug可关闭。测试进程同时有reference/被动trace，不可把整个进程RSS当某个solver实测。

重建从已计费内部KV进行，不重放forward或采样，不二读原input/output；本批核验控制/RNG保持。实际hardware时延、编译峰值、真实200B/human能力均未验。

所以本批给F层精化和固定常数下的渐近界、一个条件性cache子界，不自行激活新B/H认证或改T3。
