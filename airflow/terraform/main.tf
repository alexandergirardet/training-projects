terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

provider "google" {
  credentials = file(var.key_file)

  project = var.project
  region  = var.region
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = "training_dataset"
  description = "This is a training dataset for a mini project"
}

resource "google_storage_bucket" "auto-expire" {
  name          = var.bucket_name
  location      = var.region
  force_destroy = true

  public_access_prevention = "enforced"
}
