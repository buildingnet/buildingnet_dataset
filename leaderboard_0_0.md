<h1 align="left">BuildingNet v0.0 Benchmark Leaderboard</h1>

This is the official leaderboard of the BuildingNet v0.0 benchmark. Please email <a href="mailto:buildingnetwebmaster@gmail.com">buildingnetwebmaster@gmail.com</a>
to add or update your results.

In your email please provide the following information in this format:
```
Method, Author list, Paper title, Conference, Link to paper
Untextured Point Cloud Track, Part IoU, Shape IoU, Class acc
Textured Point Cloud Track, Part IoU, Shape IoU, Class acc
Untextured Mesh Track, Part IoU, Shape IoU, Class acc
Textured Mesh Track, Part IoU, Shape IoU, Class acc
```

<h3 align="left">Untextured Point Cloud Track</h3>

<table class="display" data-order='[[ 1, "desc" ]]'>
    <colgroup>
        <col width="30%" />
        <col width="17.5%" />
        <col width="17.5%" />
        <col width="17.5%" />
    </colgroup>
    <thead>
        <tr class="header">
            <th>Model</th>
            <th>Part IoU</th>
            <th>Shape IoU</th>
            <th>Class acc.</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td markdown="span">MinkowskiNet [2]</td>
            <td markdown="span" align="center">26.9</td>
            <td markdown="span" align="center">22.2</td>
            <td markdown="span" align="center">62.2</td>
        </tr>
    </tbody>
</table><br>

---
<br>

<h3 align="left">Textured Point Cloud Track</h3>

<table class="display" data-order='[[ 1, "desc" ]]'>
    <colgroup>
        <col width="30%" />
        <col width="17.5%" />
        <col width="17.5%" />
        <col width="17.5%" />
    </colgroup>
    <thead>
        <tr class="header">
            <th>Model</th>
            <th>Part IoU</th>
            <th>Shape IoU</th>
            <th>Class acc.</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td markdown="span">MinkowskiNet [2]</td>
            <td markdown="span" align="center">29.9</td>
            <td markdown="span" align="center">24.3</td>
            <td markdown="span" align="center">65.5</td>
        </tr>
    </tbody>
</table><br>

---
<br>

<h3 align="left">Untextured Mesh Track</h3>

<table class="display" data-order='[[ 1, "desc" ]]'>
    <colgroup>
        <col width="30%" />
        <col width="17.5%" />
        <col width="17.5%" />
        <col width="17.5%" />
    </colgroup>
    <thead>
        <tr class="header">
            <th>Model</th>
            <th>Part IoU</th>
            <th>Shape IoU</th>
            <th>Class acc.</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td markdown="span">MinkowskiNet2Triangle [2]</td>
            <td markdown="span" align="center">28.8</td>
            <td markdown="span" align="center">26.7</td>
            <td markdown="span" align="center">64.8</td>
        </tr>
        <tr>
            <td markdown="span">MinkowskiNet2Group [2]</td>
            <td markdown="span" align="center">33.1</td>
            <td markdown="span" align="center">36.0</td>
            <td markdown="span" align="center">69.9</td>
        </tr>
        <tr>
            <td markdown="span">BuildingNetGNN [1]</td>
            <td markdown="span" align="center">40.0</td>
            <td markdown="span" align="center">44.0</td>
            <td markdown="span" align="center">74.5</td>
        </tr>
    </tbody>
</table><br>

---
<br>

<h3 align="left">Textured Mesh Track</h3>

<table class="display" data-order='[[ 1, "desc" ]]'>
    <colgroup>
        <col width="30%" />
        <col width="17.5%" />
        <col width="17.5%" />
        <col width="17.5%" />
    </colgroup>
    <thead>
        <tr class="header">
            <th>Model</th>
            <th>Part IoU</th>
            <th>Shape IoU</th>
            <th>Class acc.</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td markdown="span">MinkowskiNet2Triangle [2]</td>
            <td markdown="span" align="center">32.8</td>
            <td markdown="span" align="center">29.2</td>
            <td markdown="span" align="center">68.1</td>
        </tr>
        <tr>
            <td markdown="span">MinkowskiNet2Group [2]</td>
            <td markdown="span" align="center">37.0</td>
            <td markdown="span" align="center">39.1</td>
            <td markdown="span" align="center">73.2</td>
        </tr>
        <tr>
            <td markdown="span">BuildingNetGNN [1]</td>
            <td markdown="span" align="center">42.6</td>
            <td markdown="span" align="center">46.8</td>
            <td markdown="span" align="center">77.8</td>
        </tr>
    </tbody>
</table><br>

---

<h3 align="left">References</h3>

[1] Pratheba Selvaraju, Mohamed Nabail, Marios Loizou, Maria Maslioukova, Melinos Averkiou, Andreas Andreou,
Siddhartha Chaudhuri, Evangelos Kalogerakis. <a href="https://arxiv.org/abs/2110.04955">BuildingNet: Learning to Label 3D Buildings</a>. *In Proc. ICCV*, 2021<br>
[2] Christopher Choy, JunYoung Gwak, and Silvio Savarese. <a href="https://arxiv.org/abs/1904.08755">4D Spatio-Temporal ConvNets: Minkowski Convolutional
Neural Networks</a>. *In Proc. CVPR*, 2019<br>