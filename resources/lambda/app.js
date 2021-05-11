exports.main = async (event, context) => {
  try {
    return {
      statusCode: 200,
      headers: {},
      body: JSON.stringify({"message":"greetings"})
    }
  } catch (err) {
    return { error: err }
  }
}