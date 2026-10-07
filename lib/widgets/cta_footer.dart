import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'brand_mark.dart';
import 'responsive.dart';

const _brandBlue = Color(0xFF2E6FEB);
const _brandViolet = Color(0xFF7A5BE8);

class CtaFooter extends StatelessWidget {
  const CtaFooter({super.key});

  @override
  Widget build(BuildContext context) {
    final isNarrow = screenSizeOf(context).index < ScreenSize.desktop.index;

    return Column(
      children: [
        // ----- CTA card -----
        Padding(
          padding: EdgeInsets.symmetric(
              horizontal: isNarrow ? 16 : Breakpoints.pageGutter),
          child: PageWrap(
            child: Container(
              padding: EdgeInsets.symmetric(
                horizontal: isNarrow ? 24 : 56,
                vertical: isNarrow ? 44 : 68,
              ),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(24),
                gradient: const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color(0xFF0B2A33),
                    Color(0xFF13425A),
                    Color(0xFF1E365A),
                  ],
                ),
                boxShadow: [
                  BoxShadow(
                    color: _brandBlue.withValues(alpha: 0.25),
                    blurRadius: 48,
                    offset: const Offset(0, 20),
                    spreadRadius: -16,
                  ),
                ],
              ),
              child: Stack(
                children: [
                  // Soft radial accents on top of the gradient
                  Positioned(
                    right: -40,
                    top: -40,
                    child: Container(
                      width: 200,
                      height: 200,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: RadialGradient(
                          colors: [
                            _brandViolet.withValues(alpha: 0.5),
                            Colors.transparent,
                          ],
                        ),
                      ),
                    ),
                  ),
                  Positioned(
                    left: -30,
                    bottom: -60,
                    child: Container(
                      width: 220,
                      height: 220,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: RadialGradient(
                          colors: [
                            _brandBlue.withValues(alpha: 0.5),
                            Colors.transparent,
                          ],
                        ),
                      ),
                    ),
                  ),
                  isNarrow
                      ? Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _ctaCopy(),
                            const SizedBox(height: 24),
                            _ctaActions(),
                          ],
                        )
                      : Row(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            Expanded(flex: 13, child: _ctaCopy()),
                            const SizedBox(width: 48),
                            Expanded(flex: 9, child: _ctaActions()),
                          ],
                        ),
                ],
              ),
            ),
          ),
        ),

        const SizedBox(height: 72),

        // ----- Footer -----
        Container(
          color: const Color(0xFF0A1419),
          padding: EdgeInsets.symmetric(
            horizontal: isNarrow ? 20 : Breakpoints.pageGutter,
            vertical: isNarrow ? 48 : 72,
          ),
          child: PageWrap(child: const _FooterContent()),
        ),
      ],
    );
  }

  Widget _ctaCopy() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(999),
          ),
          child: Text(
            'EARLY ACCESS · 2026',
            style: AppText.mono(size: 10, color: Colors.white).copyWith(
              letterSpacing: 1.6,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        const SizedBox(height: 18),
        Text(
          'Design the next decade\nof your planning with us.',
          style: AppText.serif(size: 34, weight: FontWeight.w500)
              .copyWith(color: Colors.white, height: 1.15),
        ),
        const SizedBox(height: 14),
        Text(
          'Reflica is in active research toward a 2027 benchmark and 2028 thesis. '
          'If you work on consequential decisions under disruption — disaster '
          'response, hospital operations, infrastructure, research planning — '
          'we would like to design with you.',
          style: AppText.body(size: 15)
              .copyWith(color: Colors.white.withValues(alpha: 0.78)),
        ),
      ],
    );
  }

  Widget _ctaActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        _OnDarkButton(
          label: 'Request access',
          icon: Icons.arrow_forward,
          primary: true,
        ),
        const SizedBox(height: 10),
        _OnDarkButton(
          label: 'Read the blueprint',
          icon: Icons.description_outlined,
          primary: false,
        ),
      ],
    );
  }
}

// -------- footer content --------

class _FooterContent extends StatelessWidget {
  const _FooterContent();

  @override
  Widget build(BuildContext context) {
    final isNarrow = screenSizeOf(context).index < ScreenSize.desktop.index;

    final brandBlock = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const BrandMark(size: 28),
            const SizedBox(width: 10),
            Text(
              'Reflica',
              style: AppText.serif(size: 22, weight: FontWeight.w600)
                  .copyWith(color: Colors.white),
            ),
          ],
        ),
        const SizedBox(height: 14),
        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 320),
          child: Text(
            'A human-centred decision-intelligence layer for AI. '
            'Living strategic planning that keeps up with reality.',
            style: AppText.body(size: 14)
                .copyWith(color: Colors.white.withValues(alpha: 0.68)),
          ),
        ),
        const SizedBox(height: 20),
        _StayInTouch(),
        const SizedBox(height: 20),
        const _SocialRow(),
      ],
    );

    final cols = <Widget>[
      _FooterCol(
        title: 'Platform',
        links: const [
          _FLink('How it works'),
          _FLink('Evidence model'),
          _FLink('In action'),
          _FLink('Research'),
          _FLink('Changelog'),
        ],
      ),
      _FooterCol(
        title: 'For',
        links: const [
          _FLink('Individuals'),
          _FLink('Organisations'),
          _FLink('Research institutions'),
          _FLink('Government'),
          _FLink('Disaster response'),
        ],
      ),
      _FooterCol(
        title: 'Company',
        links: const [
          _FLink('Blueprint', badge: 'PDF'),
          _FLink('Benchmark', badge: 'soon'),
          _FLink('Team'),
          _FLink('Press'),
          _FLink('Contact'),
        ],
      ),
      _FooterCol(
        title: 'Legal',
        links: const [
          _FLink('Privacy'),
          _FLink('Terms'),
          _FLink('DPDP Act, 2023'),
          _FLink('Security'),
          _FLink('Status'),
        ],
      ),
    ];

    final grid = isNarrow
        ? Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              brandBlock,
              const SizedBox(height: 36),
              Wrap(
                spacing: 40,
                runSpacing: 28,
                children: cols
                    .map((c) => SizedBox(width: 150, child: c))
                    .toList(),
              ),
            ],
          )
        : Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(flex: 24, child: brandBlock),
              Expanded(flex: 11, child: cols[0]),
              Expanded(flex: 11, child: cols[1]),
              Expanded(flex: 11, child: cols[2]),
              Expanded(flex: 11, child: cols[3]),
            ],
          );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        grid,
        const SizedBox(height: 48),
        Container(
          padding: const EdgeInsets.only(top: 24),
          decoration: BoxDecoration(
            border: Border(
              top: BorderSide(color: Colors.white.withValues(alpha: 0.08)),
            ),
          ),
          child: isNarrow
              ? Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _baseText(
                        '© 2026 Reflica · M.Tech research · GLA University'),
                    const SizedBox(height: 10),
                    _baseText(
                        'Built in Mathura, India. For decisions that cannot afford to be wrong.'),
                  ],
                )
              : Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _baseText(
                        '© 2026 Reflica · M.Tech research · GLA University'),
                    _baseText(
                        'Built in Mathura, India. For decisions that cannot afford to be wrong.'),
                  ],
                ),
        ),
      ],
    );
  }

  Widget _baseText(String s) => Text(
        s,
        style: AppText.mono(size: 11.5)
            .copyWith(color: Colors.white.withValues(alpha: 0.5)),
      );
}

// -------- footer column --------

class _FooterCol extends StatelessWidget {
  final String title;
  final List<_FLink> links;
  const _FooterCol({required this.title, required this.links});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title.toUpperCase(),
          style: AppText.mono(size: 10.5).copyWith(
            color: Colors.white.withValues(alpha: 0.5),
            letterSpacing: 1.6,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        ...links.map(
          (l) => Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: _FooterLink(link: l),
          ),
        ),
      ],
    );
  }
}

class _FLink {
  final String label;
  final String? badge;
  const _FLink(this.label, {this.badge});
}

class _FooterLink extends StatefulWidget {
  final _FLink link;
  const _FooterLink({required this.link});

  @override
  State<_FooterLink> createState() => _FooterLinkState();
}

class _FooterLinkState extends State<_FooterLink> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final l = widget.link;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          AnimatedDefaultTextStyle(
            duration: const Duration(milliseconds: 150),
            style: AppText.body(size: 14).copyWith(
              color: _hover
                  ? Colors.white
                  : Colors.white.withValues(alpha: 0.75),
              fontWeight: FontWeight.w500,
            ),
            child: Text(l.label),
          ),
          if (l.badge != null) ...[
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: _brandBlue.withValues(alpha: 0.22),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                l.badge!.toUpperCase(),
                style: AppText.mono(size: 9).copyWith(
                  color: Colors.white,
                  letterSpacing: 1.1,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

// -------- newsletter --------

class _StayInTouch extends StatefulWidget {
  @override
  State<_StayInTouch> createState() => _StayInTouchState();
}

class _StayInTouchState extends State<_StayInTouch> {
  final _ctrl = TextEditingController();
  bool _submitted = false;

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_submitted) {
      return Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.06),
          border:
              Border.all(color: AppColors.sage.withValues(alpha: 0.5)),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Row(
          children: [
            Icon(Icons.check_circle, color: AppColors.sage, size: 18),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                'Thanks — we\'ll be in touch.',
                style: AppText.body(size: 13).copyWith(color: Colors.white),
              ),
            ),
          ],
        ),
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'STAY IN TOUCH',
          style: AppText.mono(size: 10.5).copyWith(
            color: Colors.white.withValues(alpha: 0.5),
            letterSpacing: 1.6,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 10),
        Container(
          padding: const EdgeInsets.fromLTRB(14, 4, 4, 4),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.06),
            border:
                Border.all(color: Colors.white.withValues(alpha: 0.14)),
            borderRadius: BorderRadius.circular(999),
          ),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _ctrl,
                  onSubmitted: (_) => setState(() => _submitted = true),
                  style: AppText.body(size: 14).copyWith(color: Colors.white),
                  decoration: InputDecoration(
                    border: InputBorder.none,
                    hintText: 'you@organisation.in',
                    hintStyle: AppText.body(size: 14).copyWith(
                      color: Colors.white.withValues(alpha: 0.4),
                    ),
                    isCollapsed: true,
                    contentPadding: const EdgeInsets.symmetric(vertical: 10),
                  ),
                ),
              ),
              GestureDetector(
                onTap: () {
                  if (_ctrl.text.trim().isNotEmpty) {
                    setState(() => _submitted = true);
                  }
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Icon(Icons.arrow_forward,
                      size: 16, color: AppColors.ink),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

// -------- socials --------

class _SocialRow extends StatelessWidget {
  const _SocialRow();

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        _SocialIcon(icon: Icons.email_outlined, tooltip: 'Email'),
        const SizedBox(width: 8),
        _SocialIcon(icon: Icons.code, tooltip: 'GitHub'),
        const SizedBox(width: 8),
        _SocialIcon(icon: Icons.alternate_email, tooltip: 'X / Twitter'),
        const SizedBox(width: 8),
        _SocialIcon(icon: Icons.business, tooltip: 'LinkedIn'),
      ],
    );
  }
}

class _SocialIcon extends StatefulWidget {
  final IconData icon;
  final String tooltip;
  const _SocialIcon({required this.icon, required this.tooltip});

  @override
  State<_SocialIcon> createState() => _SocialIconState();
}

class _SocialIconState extends State<_SocialIcon> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: Tooltip(
        message: widget.tooltip,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          width: 34,
          height: 34,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: _hover
                ? Colors.white.withValues(alpha: 0.12)
                : Colors.white.withValues(alpha: 0.06),
            border: Border.all(
              color: Colors.white.withValues(alpha: _hover ? 0.3 : 0.14),
            ),
          ),
          alignment: Alignment.center,
          child: Icon(
            widget.icon,
            size: 15,
            color: Colors.white.withValues(alpha: _hover ? 1 : 0.7),
          ),
        ),
      ),
    );
  }
}

// -------- shared on-dark button --------

class _OnDarkButton extends StatefulWidget {
  final String label;
  final IconData icon;
  final bool primary;
  const _OnDarkButton({
    required this.label,
    required this.icon,
    required this.primary,
  });

  @override
  State<_OnDarkButton> createState() => _OnDarkButtonState();
}

class _OnDarkButtonState extends State<_OnDarkButton> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final isPrimary = widget.primary;
    final bg = isPrimary
        ? (_hover ? Colors.white : Colors.white)
        : (_hover
            ? Colors.white.withValues(alpha: 0.1)
            : Colors.transparent);
    final text = isPrimary ? AppColors.ink : Colors.white;

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: () {},
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding:
              const EdgeInsets.symmetric(horizontal: 22, vertical: 14),
          decoration: BoxDecoration(
            color: bg,
            border: Border.all(
              color: isPrimary
                  ? Colors.white
                  : Colors.white.withValues(alpha: 0.3),
            ),
            borderRadius: BorderRadius.circular(999),
            boxShadow: isPrimary && _hover
                ? [
                    BoxShadow(
                      color: Colors.white.withValues(alpha: 0.3),
                      blurRadius: 24,
                      spreadRadius: -4,
                    ),
                  ]
                : [],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                widget.label,
                style: AppText.body(size: 14).copyWith(
                  color: text,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(width: 10),
              Icon(widget.icon, size: 16, color: text),
            ],
          ),
        ),
      ),
    );
  }
}
