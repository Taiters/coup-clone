function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="text-center bottom-4 absolute inset-x-0 grayscale-10 text-footer">
      <span>
        © {currentYear} Dan Tait -{" "}
        <a
          className="underline"
          target="_blank"
          title="dotslashdan.com"
          href="https://dotslashdan.com"
        >
          dotslashdan.com
        </a>
      </span>
    </footer>
  );
}

export default Footer;
