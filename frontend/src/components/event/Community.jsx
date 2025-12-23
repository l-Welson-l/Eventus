import { useEffect, useState } from "react";
import {
  getEventPosts,
  createPost,
  createComment,
} from "../../api/events";

import "./Community.css"

export default function Community({ eventId }) {
  const [posts, setPosts] = useState([]);
  const [text, setText] = useState("");
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);

  const anonId = localStorage.getItem("anonymous_session_id");

  // Load posts
  useEffect(() => {
    getEventPosts(eventId).then((res) => setPosts(res.data));
  }, [eventId]);

  const submitPost = async () => {
    if (!text && !image) return;

    setLoading(true);

    const formData = new FormData();
    formData.append("text", text);
    if (image) formData.append("image", image);
    if (anonId) formData.append("anonymous_session_id", anonId);

    const res = await createPost(eventId, formData);
    setPosts([res.data, ...posts]);

    setText("");
    setImage(null);
    setLoading(false);
  };

  return (
    <section className="community">
      <h3>Community</h3>

      {/* CREATE POST */}
      <div className="create-post">
        <textarea
          placeholder="Write something..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <input
          type="file"
          onChange={(e) => setImage(e.target.files[0])}
        />

        <button onClick={submitPost} disabled={loading}>
          Post
        </button>
      </div>

      {/* POSTS */}
      <div className="posts">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} anonId={anonId} />
        ))}
      </div>
    </section>
  );
}

/* ---------------- POST CARD ---------------- */

function PostCard({ post, anonId }) {
  const [comment, setComment] = useState("");
  const [comments, setComments] = useState(post.comments || []);

  const submitComment = async () => {
    if (!comment) return;

    const res = await createComment(post.id, {
      text: comment,
      anonymous_session_id: anonId,
    });

    setComments([...comments, res.data]);
    setComment("");
  };

  return (
    <div className="post-card">
      <p>{post.text}</p>

      {post.image && (
        <img src={post.image} alt="" className="post-image" />
      )}

      {/* COMMENTS */}
      <div className="comments">
        {comments.map((c) => (
          <p key={c.id} className="comment">
            {c.text}
          </p>
        ))}
      </div>

      {/* ADD COMMENT */}
      <input
        placeholder="Write a comment..."
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />
      <button onClick={submitComment}>Comment</button>
    </div>
  );
}
