# What is Kubernetes?

Kubernetes, also known as K8s, is an open-source platform for managing containerized workloads and services. facilitates both declarative configuration and automation. It was originally designed by Google and is now maintained by the Cloud Native Computing Foundation. 

- Kubernetes orchestrates clusters of virtual machines and schedules containers to run on those virtual machines based on their available compute resources and the resource requirements of each container.
- Containers are grouped into pods, the basic operational unit for Kubernetes, and those pods scale to your desired state.
- Kubernetes also automatically manages service discovery, incorporates load balancing, tracks resource allocation, and scales based on compute utilization.


## In Summary -
Kubernetes provides a way to schedule and deploy containers, scale them to your desired state, and manage their lifecycles. It makes workloads portable and allows you to implement your container-based applications in a portable, scalable, and extensible way.


## Set up Kubernetes by installing Minikube:

*If you want to set up Kubernetes by installing Minikube, just visit the [Kubernetes Lab-Setup](https://azfaralam.hashnode.dev/kubernetes-lab-setup). In this blog, you will find a step-by-step guide from start to finish, allowing you to easily complete your Kubernetes lab setup. So, what are you waiting for? Just click on [Kubernetes Lab-Setup](https://azfaralam.hashnode.dev/kubernetes-lab-setup)**


## Basic Important Commands in Kubernetes -

1. **Creation of Pods**

    ```bash
   kubectl run azfarpod --image=httpd
   ```

2. **To check the Pods**

    ```bash
    kubectl get pods
    ```

3. **To delete a Pods**

    ```bash
    kubectl delete pods --all 
    ```
    **or**
   ```bash
   kubectl delete pods azfarpod
   ```

4. **To create a pod from a YAML code**

     ```bash
       kubectl create -f filename.yml
     ```

5. **Now, if you want to create a ReplicaSet or ReplicationController, it will be created by the YAML code only. You'll find both codes in the above repo.**

    ```bash
     kubectl create -f ymlfilename.yml
    ```

> [!NOTE]
> If you want to create anything using a YAML file, use the command with the YAML file name like 'kubectl apply -f youryamlfilename.yml'.
    


6. **To create more ReplicationController(rc) after after**

   ```bash
      kubectl scale --replicas=3 rc/azfar-replicationcontroller
   ```

    - This command is help you. Suppose you've already created only one ReplicationController, and you want to create more. In that case, you can use the above command👆
  
7.  **To check the services(svc) in cluster**

    ```bash
    kubectl get svc
    ```

18. **To create your own svc by the ReplicationController**

    ```bash
    kubectl expose --type=NodePort --port=80 rc/azfar-replication-controller
    ```

    - This configuration depends on the type you want to create. If you prefer creating it with a ClusterIP instead of a NodePort, replace it. Then, specify the type's name on the cluster. You can explore 
      more options by checking this below command 👇

       ```bash
      kubectl expose --help
        ```

9. **To see the port and much more about your services**

    ```bash
    kubectl describe svc azfar-replication-controller
    ```

10. **To Retrieve the cluster's IP address for accessing deployed services**

     ```bash
     minikube ip
     ```

11.  **TO check StorageClass**

     ```bash
      kubectl get sc
     ```
      - It retrieve information about the StorageClasses in your Kubernetes cluster. It provides details about the available storage classes, such as their name, provisioner, parameters, and other 
        relevant information.

12. **To check the PersistenceVolumeClaim**

    ```bash
     kubectl get pvc
    ```
     -  This command displays information about the PersistentVolumeClaims in the cluster. It shows details like the name of the PVC, the associated volume, the storage capacity requested and allocated, 
       the status of the claim, and more.

13. **To check only PersistenceVolume**

     ```bash
      kubectl get pv
     ```

      - It provides information about the PersistentVolumes in the cluster. It includes details such as the name of the PV, its capacity, access modes, status, and the PersistentVolumeClaim it might be 
        bound to.

14. **To check deploy**

    ```bash
     kubectl get deploy
    ```

     - is used to retrieve information about the Deployments in your Kubernetes cluster. Deployments are a higher-level abstraction for managing and updating a set of pods in your cluster.
   
15. **To see the history of rollout**

     ```bash
     kubectl rollout history deploy azfard
     ```

      - it will provide you with a historical record of deployments and revisions associated with the "azfard" Deployment. It includes information such as revision numbers, deployment status, and the 
        date and time of each deployment.

16. **To check the status of the rollout**

     ```bash
     kubectl rollout status deploy azfard
     ```

      - When you run this command, it will provide real-time information about the status of the ongoing rollout. It will show you whether the update is still in progress, has successfully completed, or 
        if there are any issues.

## What is Rollout?


In the context of Kubernetes, a "rollout" typically refers to the process of updating or rolling out a new version of an application or a set of resources in a controlled and incremental manner. The goal is to minimize downtime and ensure a smooth transition from the old version to the new one.



17. **To create new secrets and password**

     ```bash
     kubectl create secret generic azfarsecret --from-literal=p=redhat --from-literal=u=azfar
     ```

      - The kubectl create secret generic command you provided is used to create a generic secret named "azfarsecret" in Kubernetes. This secret contains two key-value pairs:

        --> key: p (for password), Value: redhat

        --> Key: u (for username), Value: azfar

          ***This command creates a secret with these key-value pairs and stores them securely in the cluster. Secrets are often used to store sensitive information such as passwords, API keys, and other 
          confidential data.***

18. **To check secrets**

     ```bash
     kubectl get secrets
     ```

      - It is used to retrieve information about the secrets in your Kubernetes cluster. When you run this command without specifying a particular secret, it will display a list of all secrets in the 
        default namespace.

19. **To check namespace**

     ```bash
     kubectl get ns
     ```

     - The kubectl get ns command is used to retrieve information about the namespaces in your Kubernetes cluster. When you run this command, it will display a list of all the namespaces along with 
       details such as the name of the namespace and its status.

       ***Namespaces in Kubernetes provide a way to organize and isolate resources within a cluster. They are particularly useful for managing and segregating applications or environments.***

20. **To check the status of clusterrole**

    ```bash
    kubectl get clusterrole
    ```

     - it will display a list of ClusterRoles along with details such as the name of the ClusterRole, the age, and other relevant information.
   
21. **To get rolebinding**

     ```bash
     kubectl get rolebinding -n testing
     ```

      - This command is used to retrieve information about RoleBindings in the specific namespace "testing" in your Kubernetes cluster. RoleBindings are used to bind roles to subjects (such as users or 
        service accounts) within a specific namespace.

22. **to test rolebinding**

     ```bash
     kubectl describe rolebinding -n testing
     ```

      - When you run this command, it will display information such as: 

         --> Name of the RoleBinding

         --> Namespace it belongs to ("testing" in this case)

         --> Role associated with the RoleBinding

         --> Subjects (users, groups, or service accounts) bound by the RoleBinding

         --> Creation timestamp

         --> Other relevant details about the RoleBinding configuration

23. **To create new configmap attaching your own port in the .txt file**

     ```bash
     kubectl create configmap azfarcm --from-file myweb.txt
     ```
      - It is used to create a ConfigMap named "azfarcm" in your Kubernetes cluster. This ConfigMap is populated with the contents of a file named "myweb.txt."
     
        --> ``kubectl create configmap`` Initiates the creation of a ConfigMap.

        --> ```azfarcm``` Specifies the name of the ConfigMap as "azfarcm."

        --> ```--from-file myweb.txt:``` Populates the ConfigMap with the contents of the "myweb.txt" file.

           - ConfigMaps are useful for storing configuration data that can be consumed by pods in a Kubernetes cluster.


## What is Kubernetes Ingress?

Kubernetes Ingress is a set of rules that manage external access to the services in a Kubernetes cluster. It is an API object that allows you to configure routing protocols, typically via HTTPS/HTTP.  By using Ingress, you can consolidate your routing rules into a single resource.

24. **To check Ingress**

    ```bash
    minikube addons enable ingress
    ```

25. **Verify that the NGINX Ingress controller is running**

    ```bash
    kubectl get pods -n ingress-nginx
    ```

> [!NOTE]
>  It can take up to a minute before you see these pods running OK.


26. **To check Ingress**

    ```bash
    kubectl get ingress
    ```
     -  It is used to retrieve information about Ingress resources in your Kubernetes cluster. Ingress is an API object that provides HTTP and HTTPS routing to services based on rules.

*To know more about the Ingress-Minikube then visit once [Kubernetes-Ingress](https://kubernetes.io/docs/tasks/access-application-cluster/ingress-minikube/) here you will get the whole command as well as yaml code also so visit once [Kubernetes-Ingress](https://kubernetes.io/docs/tasks/access-application-cluster/ingress-minikube/)*


27. **To check network policy**

     ```bash
     kubectl get networkpolicy
     ```



## Important Commands in Kubernetes which you should known about -

1. **To check the services in Kubernetes**

    ```bash
    kubectl api-resources
    ```
     - It display a list of available API resources in your Kubernetes cluster. When you run this command, it provides a list of resource types along with their short names, API group, and whether they 
       are namespaced.

2. **To get CustomResourceDefinitions**

    ```bash
    kubectl get crd
    ```
     - To retrieve information about CustomResourceDefinitions (CRDs) in your Kubernetes cluster. CRDs allow you to define custom resources and their behavior in a Kubernetes cluster, extending the API 
       and enabling the creation of custom resources.


## Keep Learning & Sharing.. ✨

 <!-- Thanks for Visiting 💚 -->
