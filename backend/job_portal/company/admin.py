from django.contrib import admin
from .models import Company, CompanyPhoto, EmployeeReview


class CompanyPhotoInline(admin.TabularInline):
    model = CompanyPhoto
    extra = 1
    readonly_fields = ('photo_url',)
    fields = ('photo_url', 'source')


class EmployeeReviewInline(admin.TabularInline):
    model = EmployeeReview
    extra = 1
    fields = ('reviewer_name', 'rating', 'title', 'review', 'is_verified')
    readonly_fields = ()


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'google_rating', 'total_google_reviews', 'founded_year', 'industry')
    search_fields = ('name', 'website', 'industry', 'founded_by')
    list_filter = ('industry', 'open_now', 'price_level')
    readonly_fields = ('google_place_id', 'fsq_id', 'created_at', 'updated_at')
    inlines = [CompanyPhotoInline, EmployeeReviewInline]


@admin.register(CompanyPhoto)
class CompanyPhotoAdmin(admin.ModelAdmin):
    list_display = ('company', 'photo_url', 'source', 'created_at')
    search_fields = ('company__name', 'source')
    readonly_fields = ('created_at',)


@admin.register(EmployeeReview)
class EmployeeReviewAdmin(admin.ModelAdmin):
    list_display = ('company', 'reviewer_name', 'rating', 'title', 'is_verified', 'created_at')
    search_fields = ('company__name', 'reviewer_name', 'title')
    list_filter = ('is_verified',)
    readonly_fields = ('created_at',)
