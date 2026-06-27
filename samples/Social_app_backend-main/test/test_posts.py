from app import schema
import pytest

def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")

    ## validating posts using schemas
    def validate(post):
        return schema.PostReturn(**post)
       
    posts_map = map(validate, res.json())
    assert res.status_code == 200


def test_unauthorized_user_get_all_posts(client):
    res = client.get("/posts/")
    assert res.status_code == 401


def test_unauthorized_user_get_one_post(client, test_posts):
    res = client.get("/posts/{test_posts[0].id}")
    assert res.status_code == 401

def test_get_nonexistant_post(test_posts, authorized_client):
    res = authorized_client.get("/posts/9999")
    assert res.status_code == 404

def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f'/posts/{test_posts[0].id}')
    ret_post = schema.PostWithVotes(**res.json())
    assert ret_post.post.id == test_posts[0].id
    assert ret_post.post.content == test_posts[0].content
    assert ret_post.post.title == test_posts[0].title
    
@pytest.mark.parametrize("title, content, published", [
    ("Going to china", "ni hao", True),
    ("Escaping from china", "BING CHILLING", False),
    ("Hello El Salvador", "Ni Chi Cho Chong", True)
])
def test_create_post(authorized_client, title, content, published, test_user):
    res = authorized_client.post("/posts", json= {"title": title, "content": content, "published": published})

    created_post = schema.PostReturn(**res.json())
    assert res.status_code == 201
    assert created_post.title == title 
    assert created_post.content == content 
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']

def test_unauthorized_client_create_post(client):
    res = client.post("/posts", json= {"title": "heeloo", "content": "SBSNF"})
    assert res.status_code == 401

def test_unauthorized_client_delete_post(client, test_user, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401

def test_delete_post_success(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 204

def test_delete_other_user_post(authorized_client, test_posts, test_user2):
    res = authorized_client.delete(f"/posts/{test_posts[2].id}")
    assert res.status_code == 403

def test_update_post(authorized_client, test_posts):
    data = {
        "title" : "updated title",
        "content" : "updated content",
        "id" : test_posts[0].id
    }

    res = authorized_client.put(f"/posts/{test_posts[0].id}", json= data)
    updated_post = schema.PostReturn(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']

def test_update_other_user_post(authorized_client, test_posts, test_user2):
    data = {
        "title" : "updated title",
        "content" : "updated content",
        "id" : test_posts[2].id
    }

    res = authorized_client.put(f"/posts/{test_posts[2].id}", json= data)
    assert res.status_code == 403

def test_unauthorized_client_update_post(client, test_user, test_posts):
    res = client.put(f"/posts/{test_posts[2].id}", json= {"title": "dont", "content": "worry"})
    assert res.status_code == 401
