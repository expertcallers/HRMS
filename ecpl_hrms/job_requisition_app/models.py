from django.db import models

class Tickets(models.Model):
    job_requisition_id = models.CharField(max_length=20,null=True,blank=True)
    created_by = models.CharField(max_length=150)
    created_by_id = models.CharField(max_length=30)
    created_date = models.DateField()
    edited_by = models.TextField(null=True,blank=True)

class JobRequisition(models.Model):
    unique_id = models.TextField(null=True,blank=True)
    manager_approval = models.BooleanField(default=False)
    created_by_rm1 = models.CharField(max_length=200,null=True,blank=True)
    created_by_rm1_id = models.CharField(max_length=30,null=True,blank=True)
    requisition_date = models.DateTimeField()
    edited_date = models.DateTimeField(null=True,blank=True)
    hc_req = models.IntegerField()
    req_raised_by = models.CharField(max_length=150)
    created_by_manager = models.CharField(max_length=150)
    created_by_manager_id = models.CharField(max_length=30)
    created_by_id = models.CharField(max_length=30)
    campaign = models.CharField(max_length=200,null=True,blank=True)
    pricing = models.CharField(max_length=50,null=True,blank=True)
    department = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    process_type_one = models.CharField(max_length=50)
    process_type_two = models.CharField(max_length=50)
    process_type_three = models.CharField(max_length=50)
    salary_rang_frm = models.IntegerField()
    salary_rang_to = models.IntegerField()
    qualification = models.CharField(max_length=100)

    other_quali = models.CharField(max_length=150,null=True,blank=True)

    skills_set = models.TextField(null=True,blank=True)
    languages = models.TextField(null=True,blank=True)

    shift_timing = models.CharField(max_length=20,null=True,blank=True)
    shift_timing_frm = models.CharField(max_length=20,null=True,blank=True)
    shift_timing_to = models.CharField(max_length=20,null=True,blank=True)

    type_of_working = models.CharField(max_length=100,null=True,blank=True)

    working_from = models.CharField(max_length=20,null=True,blank=True)
    working_to = models.CharField(max_length=20,null=True,blank=True)
    week_no_days = models.IntegerField(null=True,blank=True)

    week_from = models.CharField(max_length=20,null=True,blank=True)
    week_to = models.CharField(max_length=20,null=True,blank=True)

    requisition_type = models.CharField(max_length=50,null=True,blank=True)
    reason_for_replace = models.TextField(null=True,blank=True)
    closure_date = models.DateField(null=True, blank=True)

    candidate_name_1 = models.TextField(null=True,blank=True)
    source_1 = models.CharField(max_length=50,null=True,blank=True)
    source_emp_name_1 = models.CharField(max_length=150,null=True,blank=True)
    source_internal_emp_name_1 = models.CharField(max_length=150,null=True,blank=True)
    source_internal_emp_id_1 = models.CharField(max_length=30,null=True,blank=True)
    source_internal_campaign_name_1 = models.CharField(max_length=200,null=True,blank=True)
    source_emp_id_1 = models.CharField(max_length=20,null=True,blank=True)
    source_social_1 = models.CharField(max_length=100,null=True,blank=True)
    source_partners_1 = models.CharField(max_length=100,null=True,blank=True)
    interviewer1 = models.CharField(max_length=100,null=True,blank=True)

    candidate_name_2 = models.TextField(null=True,blank=True)
    source_2 = models.CharField(max_length=50,null=True,blank=True)
    source_emp_name_2 = models.CharField(max_length=150,null=True,blank=True)
    source_emp_id_2 = models.CharField(max_length=20,null=True,blank=True)
    source_internal_emp_name_2 = models.CharField(max_length=150, null=True, blank=True)
    source_internal_emp_id_2 = models.CharField(max_length=30, null=True, blank=True)
    source_internal_campaign_name_2 = models.CharField(max_length=200, null=True, blank=True)
    source_social_2 = models.CharField(max_length=100,null=True,blank=True)
    source_partners_2 = models.CharField(max_length=100,null=True,blank=True)
    interviewer_2 = models.CharField(max_length=100,null=True,blank=True)


    candidate_name_3 = models.TextField(null=True,blank=True)
    source_3 = models.CharField(max_length=50,null=True,blank=True)
    source_emp_name_3 = models.CharField(max_length=150,null=True,blank=True)
    source_emp_id_3 = models.CharField(max_length=20,null=True,blank=True)
    source_internal_emp_name_3 = models.CharField(max_length=150, null=True, blank=True)
    source_internal_emp_id_3 = models.CharField(max_length=30, null=True, blank=True)
    source_internal_campaign_name_3 = models.CharField(max_length=200, null=True, blank=True)
    source_social_3 = models.CharField(max_length=100,null=True,blank=True)
    source_partners_3 = models.CharField(max_length=100,null=True,blank=True)
    interviewer_3 = models.CharField(max_length=100,null=True,blank=True)


    candidate_name_4 = models.TextField(null=True,blank=True)
    source_4 = models.CharField(max_length=50,null=True,blank=True)
    source_emp_name_4 = models.CharField(max_length=150,null=True,blank=True)
    source_emp_id_4 = models.CharField(max_length=20,null=True,blank=True)
    source_internal_emp_name_4 = models.CharField(max_length=150, null=True, blank=True)
    source_internal_emp_id_4 = models.CharField(max_length=30, null=True, blank=True)
    source_internal_campaign_name_4 = models.CharField(max_length=200, null=True, blank=True)
    source_social_4 = models.CharField(max_length=100,null=True,blank=True)
    source_partners_4 = models.CharField(max_length=100,null=True,blank=True)
    interviewer_4 = models.CharField(max_length=100,null=True,blank=True)


    candidate_name_5 = models.TextField(null=True,blank=True)
    source_5 = models.CharField(max_length=50,null=True,blank=True)
    source_emp_name_5 = models.CharField(max_length=150,null=True,blank=True)
    source_emp_id_5 = models.CharField(max_length=20,null=True,blank=True)
    source_internal_emp_name_5 = models.CharField(max_length=150, null=True, blank=True)
    source_internal_emp_id_5 = models.CharField(max_length=30, null=True, blank=True)
    source_internal_campaign_name_5 = models.CharField(max_length=200, null=True, blank=True)
    source_social_5 = models.CharField(max_length=100,null=True,blank=True)
    source_partners_5 = models.CharField(max_length=100,null=True,blank=True)
    interviewer_5 = models.CharField(max_length=100,null=True,blank=True)


    candidate_name_6 = models.TextField(null=True,blank=True)
    source_6 = models.CharField(max_length=50,null=True,blank=True)
    source_emp_name_6 = models.CharField(max_length=150,null=True,blank=True)
    source_emp_id_6 = models.CharField(max_length=20,null=True,blank=True)
    source_internal_emp_name_6 = models.CharField(max_length=150, null=True, blank=True)
    source_internal_emp_id_6 = models.CharField(max_length=30, null=True, blank=True)
    source_internal_campaign_name_6 = models.CharField(max_length=200, null=True, blank=True)
    source_social_6 = models.CharField(max_length=100,null=True,blank=True)
    source_partners_6 = models.CharField(max_length=100,null=True,blank=True)
    interviewer_6 = models.CharField(max_length=100,null=True,blank=True)


    candidate_name_7 = models.TextField(null=True,blank=True)
    source_7 = models.CharField(max_length=50,null=True,blank=True)
    source_emp_name_7 = models.CharField(max_length=150,null=True,blank=True)
    source_emp_id_7 = models.CharField(max_length=20,null=True,blank=True)
    source_internal_emp_name_7 = models.CharField(max_length=150, null=True, blank=True)
    source_internal_emp_id_7 = models.CharField(max_length=30, null=True, blank=True)
    source_internal_campaign_name_7 = models.CharField(max_length=200, null=True, blank=True)
    source_social_7 = models.CharField(max_length=100,null=True,blank=True)
    source_partners_7 = models.CharField(max_length=100,null=True,blank=True)
    interviewer_7 = models.CharField(max_length=100,null=True,blank=True)


    candidate_name_8 = models.TextField(null=True,blank=True)
    source_8 = models.CharField(max_length=50,null=True,blank=True)
    source_emp_name_8 = models.CharField(max_length=150,null=True,blank=True)
    source_emp_id_8 = models.CharField(max_length=20,null=True,blank=True)
    source_internal_emp_name_8 = models.CharField(max_length=150, null=True, blank=True)
    source_internal_emp_id_8 = models.CharField(max_length=30, null=True, blank=True)
    source_internal_campaign_name_8 = models.CharField(max_length=200, null=True, blank=True)
    source_social_8 = models.CharField(max_length=100,null=True,blank=True)
    source_partners_8 = models.CharField(max_length=100,null=True,blank=True)
    interviewer_8 = models.CharField(max_length=100,null=True,blank=True)


    candidate_name_9 = models.TextField(null=True,blank=True)
    source_9 = models.CharField(max_length=50,null=True,blank=True)
    source_emp_name_9 = models.CharField(max_length=150,null=True,blank=True)
    source_emp_id_9 = models.CharField(max_length=20,null=True,blank=True)
    source_internal_emp_name_9 = models.CharField(max_length=150, null=True, blank=True)
    source_internal_emp_id_9 = models.CharField(max_length=30, null=True, blank=True)
    source_internal_campaign_name_9 = models.CharField(max_length=200, null=True, blank=True)
    source_social_9 = models.CharField(max_length=100,null=True,blank=True)
    source_partners_9 = models.CharField(max_length=100,null=True,blank=True)
    interviewer_9 = models.CharField(max_length=100,null=True,blank=True)


    candidate_name_10 = models.TextField(null=True,blank=True)
    source_10 = models.CharField(max_length=50,null=True,blank=True)
    source_emp_name_10 = models.CharField(max_length=150,null=True,blank=True)
    source_emp_id_10 = models.CharField(max_length=20,null=True,blank=True)
    source_internal_emp_name_10 = models.CharField(max_length=150, null=True, blank=True)
    source_internal_emp_id_10 = models.CharField(max_length=30, null=True, blank=True)
    source_internal_campaign_name_10 = models.CharField(max_length=200, null=True, blank=True)
    source_social_10 = models.CharField(max_length=100,null=True,blank=True)
    source_partners_10 = models.CharField(max_length=100,null=True,blank=True)
    interviewer_10 = models.CharField(max_length=100,null=True,blank=True)


    send_mail_1 = models.BooleanField(default=False)
    send_mail_2 = models.BooleanField(default=False)
    send_mail_3 = models.BooleanField(default=False)
    send_mail_4 = models.BooleanField(default=False)
    send_mail_5 = models.BooleanField(default=False)
    send_mail_6 = models.BooleanField(default=False)
    send_mail_7 = models.BooleanField(default=False)
    send_mail_8 = models.BooleanField(default=False)
    send_mail_9 = models.BooleanField(default=False)
    send_mail_10 = models.BooleanField(default=False)
    
    interviewer_id_1 = models.CharField(max_length=20, null=True, blank=True)
    interviewer_id_2 = models.CharField(max_length=20, null=True, blank=True)
    interviewer_id_3 = models.CharField(max_length=20, null=True, blank=True)
    interviewer_id_4 = models.CharField(max_length=20, null=True, blank=True)
    interviewer_id_5 = models.CharField(max_length=20, null=True, blank=True)
    interviewer_id_6 = models.CharField(max_length=20, null=True, blank=True)
    interviewer_id_7 = models.CharField(max_length=20, null=True, blank=True)
    interviewer_id_8 = models.CharField(max_length=20, null=True, blank=True)
    interviewer_id_9 = models.CharField(max_length=20, null=True, blank=True)
    interviewer_id_10 = models.CharField(max_length=20, null=True, blank=True)
   

    dead_line = models.DateField(null=True,blank=True)

    closed_by = models.CharField(max_length=150,null=True,blank=True)
    closed_by_id = models.CharField(max_length=30,null=True,blank=True)

    recruited_people = models.IntegerField(null=True,blank=True)
    reason_for_deleting = models.TextField(null=True,blank=True)
    deletion = models.BooleanField(default=False)
    ticket_status = models.BooleanField(default=True)
    request_status = models.CharField(max_length=100, default="Pending")
    candidate_remark = models.TextField(null=True,blank=True)
    initial_status = models.BooleanField(default=False)
    final_status = models.BooleanField(default=False)
    ticket_id = models.OneToOneField(Tickets,null=True,blank=True,on_delete=models.CASCADE)


