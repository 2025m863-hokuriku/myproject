from django.db import models
from django.contrib.auth.models import User
from datetime import date

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', '男性'),
        ('F', '女性'),
    ]

    ACTIVITY_CHOICES = [
        (1.2, '座り仕事が多い(運動なし)'),           
        (1.375, '軽い運動(週1-3回)'),              
        (1.55, '中程度の運動(週3-5回)'),          
        (1.725, '活発な運動(週6-7回)'),           
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="性別")
    height = models.FloatField(help_text="単位: cm", verbose_name="身長")
    weight = models.FloatField(help_text="単位: kg", verbose_name="体重")
    birth_date = models.DateField(verbose_name="生年月日")

    activity_level = models.FloatField(
        default=1.2, 
        choices=ACTIVITY_CHOICES, 
        verbose_name="活動レベル"
    )

    def get_age(self):
        today = date.today()
        if self.birth_date > today:
            return 0
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def calculate_bmr(self):
        age = self.get_age()
        if self.gender == 'M':
            bmr = (10 * self.weight) + (6.25 * self.height) - (5 * age) + 5
        else:
            bmr = (10 * self.weight) + (6.25 * self.height) - (5 * age) - 161
        return round(bmr, 0)

    def calculate_suggested_calories(self, goal='maintain'):
        tdee = self.calculate_bmr() * self.activity_level
        if goal == 'lose':
            return round(tdee - 500, 0)
        elif goal == 'gain':
            return round(tdee + 500, 0)
        return round(tdee, 0)

    def __str__(self):
        return f"{self.user.username} のプロフィール"  

class ExerciseLog(models.Model):
    MET_VALUES = {
        'running': 8.0,
        'swimming': 6.0,
        'cycling': 7.5,
        'walking': 3.0,
        'yoga': 3.0,
        'weightlifting': 3.5,
    }
    
    EXERCISE_CHOICES = [
        ('running', 'ランニング'),
        ('swimming', '水泳'),
        ('cycling', 'サイクリング'),
        ('walking', 'ウォーキング'),
        ('yoga', 'ヨガ'),
        ('weightlifting', '筋トレ'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_CHOICES)
    duration_minutes = models.IntegerField(help_text="単位: 分")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def calories_burned(self):
        try:
            profile = self.user.userprofile
            weight = profile.weight
        except Exception:
            weight = 60 
        
        met = self.MET_VALUES.get(self.exercise_type, 1)
        duration_hours = self.duration_minutes / 60.0
        
        return round(met * weight * duration_hours, 0)

