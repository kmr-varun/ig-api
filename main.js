function searchUser(data) {
  username = data.value;
  getData(username);
}

function getData(username) {
  if (username != "") {
    const apiUrl = "http://127.0.0.1:5000/user/" + username;

    const xhttpr = new XMLHttpRequest();
    xhttpr.open("GET", apiUrl, true);

    xhttpr.send();

    xhttpr.onload = () => {
      if (xhttpr.status === 200) {
        const response = JSON.parse(xhttpr.response);
        parseData(response);
      } else {
        console.log("Error");
      }
    };
  }
}

function parseData(data) {
  const username = data["username"];
  const name = data["name"];
  const followers = data["followers"];
  const follows = data["follows"];
  const profileImage = data["profile_image"];
  const video_count = data["video_count"];
  const image_count = data["image_count"];
  document.getElementById("name").innerText = name;
  //   document.getElementById("profile_img").src = profileImage;
  document.getElementById("about_field").innerHTML =
    "<span><b>username: </b>" +
    username +
    "</span>  | " +
    " <span><b>followers: </b>" +
    followers +
    "</span>  | " +
    " <span><b>follows: </b>" +
    follows +
    "</span>  | " +
    " <span><b>videos: </b>" +
    video_count +
    "</span>  | " +
    " <span><b>images: </b>" +
    image_count +
    "</span>";
}
