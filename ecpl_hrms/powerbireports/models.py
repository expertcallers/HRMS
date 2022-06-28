from django.contrib.auth.models import User
from django.db import models


class Campaign(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    campaign = models.CharField(max_length=200)
    campaignid = models.CharField(max_length=200)
    campaign_type = models.CharField(max_length=50, blank=True, null=True)
    campaign_status = models.BooleanField(default=True)
    pc = models.BooleanField(default=False)

    def __str__(self):
        return self.campaign + " - " + self.campaignid

class Mapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)

class CampaignLinks(models.Model):
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE)
    link = models.CharField(max_length=300)