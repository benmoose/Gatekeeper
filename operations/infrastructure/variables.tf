variable "aws_profile" {
  type = string
  default = "default"
}

variable "region" {
  type = string
}

variable "stack" {
  type    = string
  default = "staging"
  description = "Which environment to launch infrastrucutre into."
}
