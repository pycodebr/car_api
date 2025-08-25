resource "flux_bootstrap_git" "this" {
  embedded_manifests = true
  path               = "clusters/${module.eks.cluster_name}"
}