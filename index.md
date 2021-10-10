<p align="center">
  <a href="https://www.linkedin.com/in/prathebaselvaraju">Pratheba Selvaraju</a><sup>1</sup> &emsp;
  Mohamed Nabail<sup>1</sup> &emsp;
  <a href="https://www.cyens.org.cy/en-gb/about/people/research-department/multidisciplinary-research-groups/mrg-groups/vcg-visual-computing-group/marios-loizou/">Marios Loizou</a><sup>2</sup> &emsp;
  Maria Maslioukova<sup>2</sup> &emsp;
  <br>
  <a href="https://www.cyens.org.cy/en-gb/about/people/research-department/multidisciplinary-research-groups/mrg-groups/vcg-visual-computing-group/melinos-averkiou-1/">Melinos Averkiou</a><sup>2</sup> &emsp;
  Andreas Andreou<sup>2</sup> &emsp;
  <a href="https://www.cse.iitb.ac.in/~sidch/">Siddhartha Chaudhuri</a><sup>3</sup> &emsp;
  <a href="https://people.cs.umass.edu/~kalo/">Evangelos Kalogerakis</a><sup>1</sup>
  <br>
  <br>
  <sup>1</sup>UMass Amherst &emsp;
  <sup>2</sup>University of Cyprus / CYENS CoE &emsp;
  <sup>3</sup>Adobe Research / IIT Bombay
</p>
<br>

<div align="center">
    <img src="images/teaser.png" width="100%" height ="50%" alt="teaser.png" />
</div>

<h1 align="left">Abstract</h1>
<p align="justify">We introduce BuildingNet: (a) a large-scale dataset of 3D building models whose exteriors are consistently labeled, and (b) a graph neural network that labels building meshes by analyzing spatial and structural relations of their geometric primitives. To create our dataset, we used crowdsourcing combined with expert guidance, resulting in 513K annotated mesh primitives, grouped into 292K semantic part components across 2K building models. The dataset covers several building categories, such as houses, churches, skyscrapers, town halls, libraries, and castles. We include a benchmark for evaluating mesh and point cloud labeling. Buildings have more challenging structural complexity compared to objects in existing benchmarks (e.g., ShapeNet, PartNet), thus, we hope that our dataset can nurture the development of algorithms that are able to cope with such large-scale geometric data for both vision and graphics tasks e.g., 3D semantic segmentation, part-based generative models, correspondences, texturing, and analysis of point cloud data acquired from real-world buildings. Finally, we show that our mesh-based graph neural network significantly improves performance over several baselines for labeling 3D meshes.</p>

<h1 align="left">Paper</h1>
<a href="https://drive.google.com/file/d/1aD5AIkx58k7EyK8Utg8vKv2Y_UMZ--pv/view?usp=sharing"><img style="padding: 10px 10px 10px 10px; box-shadow:4px 4px 8px #000; float: right" width="150" src="images/thumbnail_page_01.png"></a>
<a href="https://drive.google.com/file/d/1aD5AIkx58k7EyK8Utg8vKv2Y_UMZ--pv/view?usp=sharing">BuildingNet.pdf</a>, 17.3MB
<h3 align="left">Citation</h3>
<p style="padding-right: 10px" align="left">Pratheba Selvaraju, Mohamed Nabail, Marios Loizou, Maria Maslioukova, Melinos Averkiou, Andreas Andreou, Siddhartha Chaudhuri, Evangelos Kalogerakis, "BuildingNet: Learning to Label 3D Buildings", <em>Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)</em>, 2021</p>
<br>
<a href="https://drive.google.com/file/d/1LqCN82l9zYjtjYlPM-2_tQIYWFowOMo0/view?usp=sharing">Bibtex</a>

```
@inproceedings{Selvaraju:2021:BuildingNet, 
  author = {Pratheba Selvaraju and Mohamed Nabail and Marios Loizou and Maria Maslioukova and
            Melinos Averkiou and Andreas Andreou and Siddhartha Chaudhuri and Evangelos Kalogerakis},
  title = {BuildingNet: Learning to Label 3D Buildings},   
  booktitle = {IEEE/CVF International Conference on Computer Vision (ICCV)},
  year = {2021}   
}   
```

<p align="justify"><small>Additional supplementary material: a few video examples of UI operations used for labeling - <a href="https://drive.google.com/file/d/1zpX1a0osTZyvALw0BdaTTjbY3HzsSMJQ/view?usp=sharing">video_UI_tutorial_parts.zip</a></small></p>

<h1 align="left">Dataset and Code</h1>
<p align="justify">The official implementation can be found in our <a href="https://github.com/buildingnet/buildingnet_dataset">github repository</a>. Please fill in <a href="https://forms.gle/jFQpoRzRkrTCaTzX8">this form</a>, in order to get access to the official release of the BuildingNet dataset.</p>
