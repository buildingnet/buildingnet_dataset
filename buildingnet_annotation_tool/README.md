
## **Update with database credentials**
* adminhits.php - Line 10 (admin credentials), Line 13
* admin_labelling.php - Line 19
* admin_rewritehit.php - Line 4
* final.php - Line 14
* find_distinct_labels.php - Line 15
* get_label_info_json.php - Line 12
* get_labelled_objects.php - Line 12
* get_labels.php - Line 10
* index.php - Line 38
* index_withoutvideo.php - Line 38
* labelling_withworkerid.php - Line 30
* update_get_userinfo.php - Line 16
* update_label_json.php - Line 54


### **admin_labelling.php**:
* Line 58 : update the admin_modeldata.txt under data folder 
          (update with files under js/meshes directory).
          This is used for debugging and only the files listed will be shown in the annotation tool

### **adminhits.php**:
* Line: 46,66 : Running this file with gives the results from the sql results in this line.
(can be changed to check the results desired)
* Line 408 : update with admin username and password


delete admin_label_hits.txt file in case the website would not load
(since we prevent same user login multiple times)

## **main files that holds the logic: (under 'js' folder)**
* main.js
* View.js
* LabelsManager.js
* category.js
