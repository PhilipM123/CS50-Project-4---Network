document.addEventListener('DOMContentLoaded', function(){

    let posts = document.querySelectorAll(".post");


    posts.forEach(post => {
        const editBtn = post.querySelector(".edit_btn");
        const likeBtn = post.querySelector(".like_btn");

        if(likeBtn){
            const likeDiv = post.querySelector(".like_div");
            const id = likeDiv.querySelector("*[name=id]").value; 

            likeBtn.onclick = async function(){
                console.log(`Like btn pressed id=${id}`);
                let csrftoken = post.querySelector("input[name='csrfmiddlewaretoken']").value;
                
                    const response = await fetch(`/like_posts/${id}`, {
                        method : "PUT",
                        headers: {
                            "X-CSRFToken": csrftoken
                        }
                      })
                    const data = await response.json();
                    const rawLikes = data.post.likers;
                    console.log(rawLikes);  ``
                    const likes = rawLikes.length;
                    const likeshtml = post.querySelector(".likes");
                    likeshtml.innerHTML = `Likes: ${likes}`;
            };
        }
        if (editBtn) {
            const editForm = post.querySelector("form.edit_post");
            const contentInput = editForm.querySelector("*[name=content]");
    
            editBtn.onclick = function(){
                post.classList.add("editing");
                contentInput.value = "";
                contentInput.focus();
            };
    
            async function handleSubmit(e){
                e.preventDefault();
                const id = e.target.querySelector("*[name=id]").value;
                const content = contentInput.value;
                let csrftoken = this.querySelector("input[name='csrfmiddlewaretoken']").value;
                const body = { content };
    
                try {
                    const response = await fetch(`/edit_post/${id}`, {
                        method : 'PUT',
                        body : JSON.stringify(body),
                        headers: {
                            "X-CSRFToken": csrftoken
                        }
                    })
    
                    const data = await response.json();
                    const contentElement = post.querySelector(".content");
                    contentElement.textContent = data.post.content;
                    post.classList.remove("editing");
                } catch(err) {
                    console.log(err)
                }
            }
            if (editForm) {
                editForm.addEventListener("submit", handleSubmit);
            }
        }
    })
});
