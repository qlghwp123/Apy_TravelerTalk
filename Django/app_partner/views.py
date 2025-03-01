from datetime import datetime
import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout
from django.db.models import Q
from django.conf import settings

from app_core import models
from app_core import daos

# 관리자 로그인
def login(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기

  # 파트너 계정인 경우, 파트너 관리 페이지로 이동
  if contexts['account']['account_type'] == 'partner':
    return redirect('/partner')

  return render(request, 'login.html')

# 파트너 관리자 메인 페이지
def index(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기

  if contexts['account']['account_type'] != 'partner': # 파트너 계정이 아닌 경우
    return redirect('/') # 로그인 페이지로 리다이렉트

  # 사용자 프로필 정보
  profile = daos.get_user_profile_by_id(contexts['account']['id'])

  # 파트너 계정이 소유한 여행지 게시글
  p = models.POST.objects.filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).first()
  post = daos.get_post_info(p.id)

  return render(request, 'partner/index.html', {
    **contexts,
    'profile': profile, # 사용자 프로필 정보
    'post': post, # 여행지 게시글 정보
  })
'''
# 새 광고 게시글 작성 페이지*사용하지 않음
def write_post(request):
  return redirect('/partner?redirect_message=not_use')

  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기

  if contexts['account']['account_type'] != 'partner': # 파트너 계정이 아닌 경우
    return redirect('/?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 광고 게시글이 이미 있는 경우, 광고 게시글 수정 페이지로 이동
  p = models.POST.objects.filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).first()
  if p: # 여행지 게시글이 있는 경우
    return redirect('/rewrite_post?redirect_message=travel_post_exist')

  # 광고 게시글 작성

  if request.method == 'POST':
    title = request.POST.get('title', '')
    content = request.POST.get('content', '')
    images = request.POST.get('images', '')
    board_id = request.POST.get('board_ids', '') # 게시판 ID(여러 개일 수 있음)

    # 새 광고 정책 생성
    ad = post_mo.AD(
      status='expired',
      weight=0,
      note='',
      post_id='',
    )
    ad.save()

    # 광고 게시글 생성
    post = post_mo.POST(
      board_id=board_id,
      ad_id=ad.id,
      author_id=request.user.username,
      title=title,
      content=content,
      images=images,
    )
    post.save()

    ad.post_id = post.id
    ad.save()

    # 사용자 활동 기록
    act = models.ACTIVITY(
      user_id=request.user.username,
      location='/post/travel_view?post=' + str(post.id),
      message='[파트너] 광고 게시글 작성. (' + title + ')',
      point_change=0,
    )
    act.save()

    return JsonResponse({
      'result': 'success',
      'post_id': post.id,
    })

  # 게시판 정보
  boards = daos.get_board_tree()

  # 카테고리 정보
  categories = daos.get_category_tree()

  return render(request, 'partner/write_post.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'categories': categories, # 카테고리 정보
  })
'''

# 광고 게시글 수정 페이지
def rewrite_post(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기

  if contexts['account']['account_type'] != 'partner': # 파트너 계정이 아닌 경우
    logout(request)
    return redirect('/') # 로그인 페이지로 리다이렉트
  if contexts['account']['status'] != 'active': # 파트너 계정이 활성화 상태가 아닌 경우
    return redirect('/partner/partner?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 광고 게시글 정보
  p = models.POST.objects.filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).first()
  if not p: # 여행지 게시글이 없는 경우, 기본 여행지 게시글 생성
    # 여행지 게시글 생성
    post = models.POST(
      author=request.user, # 작성자
      title='파트너사 ' + request.user.last_name + '의 여행지 정보', # 제목
      content='파트너사 ' + request.user.last_name + '의 여행지 정보입니다.', # 내용
    )
    post.save()
    # 게시글 여행지 정보 생성
    place_info = models.PLACE_INFO(
      post=post, # 게시글
      address='여행지 주소', # 주소
      location_info='여행지를 찾기위한 간단한 안내입니다.', # 위치 정보
      open_info='여행지의 영업 시간입니다.', # 영업 정보
      status='writing' # 상태
    )
    place_info.save()
    post.place_info = place_info
    post.save()
    p = post

  post = daos.get_post_info(p.id)
  post['image'] = str(post['image'])[6:]

  # 광고 게시글 작성지 확인
  if contexts['account']['id'] != post['author']['id']:  # 광고 게시글 작성자가 아닌 경우
    return redirect('/partner/partner?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 광고 게시글 수정
  if request.method == 'POST':
    po = models.POST.objects.select_related('place_info').get(id=post['id'])

    title = request.POST.get('title', po.title)
    content = str(request.POST.get('content', po.content)).replace('`', "'")
    board_ids = str(request.POST.get('board_ids')).split(',') # 게시판 ID(여러 개일 수 있음)
    service_ids = str(request.POST.get('service_ids')).split(',') # 서비스 ID(여러 개일 수 있음)
    location_info = request.POST.get('location_info', po.place_info.location_info)
    open_info = request.POST.get('open_info', po.place_info.open_info)
    address = request.POST.get('address', po.place_info.address)
    place_status = request.POST.get('place_status')
    image = request.FILES.get('image', post['image'])

    # 만약 기존 광고 상태가 'ad'인 경우, 광고 상태 유지
    if po.place_info.status == 'ad':
      place_status = 'ad'

    # 이미지가 없는 경우, 기존 이미지 유지
    if image:
      po.image = image

    # 광고 게시글 수정
    po.title = title
    po.content = content
    po.save()
    po.place_info.location_info = location_info
    po.place_info.open_info = open_info
    po.place_info.address = address
    po.place_info.status = place_status
    po.place_info.save()

    # 게시판 정보 수정
    if board_ids != ['']:
      po.boards.clear()
      for board_id in board_ids:
        board = models.BOARD.objects.get(id=int(board_id))
        po.boards.add(board)

    # 서비스 정보 수정
    if service_ids != ['']:
      po.place_info.categories.clear()
      for service_id in service_ids:
        service = models.CATEGORY.objects.get(id=service_id)
        po.place_info.categories.add(service)
    po.save()
    po.place_info.save()

    # 사용자 활동 기록
    models.ACTIVITY.objects.create(
      account=request.user,
      message='[파트너] 여행지 게시글을 수정했습니다. (' + title + ')',
    )

    return JsonResponse({
      'result': 'success',
      'post_id': po.id,
    })

  # 게시판 정보
  boards = daos.get_travel_board_tree()

  # 카테고리 정보
  categories = daos.get_category_tree()

  return render(request, 'partner/rewrite_post.html', {
    **contexts,
    'post': post, # 여행지 게시글 정보
    'boards': boards, # 게시판 정보
    'categories': categories, # 카테고리 정보
  })

# 쿠폰 관리 페이지
def coupon(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기

  if contexts['account']['account_type'] != 'partner': # 파트너 계정이 아닌 경우
    logout(request)
    return redirect('/') # 로그인 페이지로 리다이렉트
  if contexts['account']['status'] != 'active': # 파트너 계정이 활성화 상태가 아닌 경우
    return redirect('/partner/partner?redirect_message=partner_status_error')

  # 여행지 게시글
  p = models.POST.objects.filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).first()
  if not p: # 여행지 게시글이 없는 경우, 광고 게시글 작성 페이지로 이동
    return redirect('/partner/partner?redirect_message=travel_post_not_exist') # 홈으로 리다이렉트
  post = daos.get_post_info(p.id)

  # 데이터 가져오기
  tab = request.GET.get('tab', 'coupon') # coupopn, history
  page = int(request.GET.get('page', 1))
  search_coupon_code = request.GET.get('code', '') # 쿠폰 이름 검색
  search_coupon_name = request.GET.get('name', '') # 쿠폰 소유자 검색

  # 쿠폰 목록 가져오기
  if tab == 'coupon': # 쿠폰 목록
    cps = models.COUPON.objects.select_related('post', 'create_account').prefetch_related('own_accounts').filter(
      create_account=request.user,
      name__contains=search_coupon_name,
      code__contains=search_coupon_code,
      status='active',
    ).order_by('-expire_at')
  elif tab == 'history': # 쿠폰 사용 내역
    cps = models.COUPON.objects.select_related('post', 'create_account').prefetch_related('own_accounts').exclude(
      status='active',
    ).filter(
      create_account=request.user,
      name__contains=search_coupon_name,
      code__contains=search_coupon_code,
    ).order_by('-expire_at')
  coupons = []
  last_page = len(cps) // 30 + 1 # 한 페이지당 30개씩 표시
  for cp in cps[(page - 1) * 30:page * 30]:
    own_account = [{
      'id': oa.username,
      'nickname': oa.first_name,
      'status': 'active'
    } for oa in cp.own_accounts.all()]
    use_accounts = [{
      'id': ua.username,
      'nickname': ua.first_name,
      'status': 'used'
    } for ua in cp.used_account.all()]

    coupons.append({
      'code': cp.code,
      'name': cp.name,
      'image': str(cp.image) if cp.image else None,
      'content': cp.content,
      'required_mileage': cp.required_mileage,
      'expire_at': datetime.strftime(cp.expire_at, '%Y-%m-%d'),
      'created_at': cp.created_at,
      'status': cp.status,
      'note': cp.note,
      'accounts': {
        'own': own_account,
        'use': use_accounts,
      },
      'post': {
        'id': cp.post.id,
        'title': cp.post.title,
      },
      'create_account': {
        'id': cp.create_account.username,
        'nickname': cp.create_account.first_name,
      },
    })

  return render(request, 'partner/coupon.html', {
    **contexts,
    'post': post, # 여행지 게시글 정보
    'coupons': coupons, # 쿠폰 정보
    'last_page': last_page, # page 처리 작업에 사용(반드시 필요)
  })