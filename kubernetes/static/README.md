# Deploy da aplicação local

## Deploy do NGINX ingress

```
kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml
```

De acordo com a [documentação](https://kind.sigs.k8s.io/docs/user/ingress#ingress-nginx).

## Load das imagens para os nodes do Kubernetes

```
$ kind load docker-image car-api:latest
$ kind load docker-image car-api-mkdocs:latest
```

## Deploy dos manifestos

```
$ kubectl apply -f kubernetes/static
```

## Adicionar DNS no /etc/hosts

Encontre o IP do serviço de LoadBalancer do NGINX:

```
$ kubectl get svc -n ingress-nginx ingress-nginx-controller -ojson | jq -r '.status.loadBalancer.ingress[].ip'
172.18.0.5
```

Com esse IP, edite o `/etc/hosts`.

```
172.18.0.5      car-api.localhost.com car-api-mkdocs.localhost.com
```

## Ser feliz

```
$ curl car-api.localhost.com
$ curl car-api-mkdocs.localhost.com
```