provider "aws" {
  profile = var.profile
  region = var.region
}

resource "aws_load_balancer_policy" "" {
  load_balancer_name = ""
  policy_name = ""
  policy_type_name = ""
}

resource "aws_ecs_cluster" "" {
  name = ""
}
