locals {
  profile = "mateusmuller"
}

terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.9.0"
    }
    flux = {
      source  = "fluxcd/flux"
      version = "1.6.4"
    }
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      args        = ["--profile", local.profile, "eks", "get-token", "--cluster-name", module.eks.cluster_name]
      command     = "aws"
    }
  }
}

provider "aws" {
  profile = local.profile
}

provider "flux" {
  kubernetes = {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    exec = {
      api_version = "client.authentication.k8s.io/v1beta1"
      args        = ["--profile", local.profile, "eks", "get-token", "--cluster-name", module.eks.cluster_name]
      command     = "aws"
    }
  }
  git = {
    url = "ssh://git@gitlab.com/mateusmuller2/gitops.git"
    ssh = {
      username    = "git"
      private_key = file("~/.ssh/id_ed25519")
    }
  }
}